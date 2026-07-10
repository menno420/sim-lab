#!/usr/bin/env python3
"""INTAKE 002 - Discord OAuth trust-gate adversarial verification (spike + JUDGMENT-ONLY).

Method: MEASURED PROTOTYPE / SPIKE (ladder rung 2) for the executable attack suite,
plus explicitly-labelled JUDGMENT-ONLY structured analysis (rung 3) for threats that
cannot be exercised from this environment (live Discord IdP behaviour, network MITM,
hosting/secret posture, the unbuilt superbot read-only API).

WHAT THIS SETTLES (executed, reproducible, multi-seed, swept):
  A runnable model of the Discord authorization-code OAuth trust-gate described in the
  source idea's SECTION 5, with a REFERENCE implementation of each of the six SECTION 5
  controls, then an adversarial attack suite run against it. Each attack is an executed
  request sequence with an asserted expected outcome. If every listed SECTION 5 control
  is implemented as modelled, each modelled attack is DEFEATED. Two attack classes
  surface HOLES in the terse design (stale guild membership; over-broad `guilds` read).

WHAT IT DOES NOT SETTLE (JUDGMENT-ONLY / needs-live-test, see REPORT.md):
  - SECTION 5 is a CHECKLIST, not a spec: the concrete controls attacked here are THIS
    spike's reference reconstruction, not the owner's (unwritten) implementation.
  - Live Discord IdP enforcement (redirect_uri exact-match, code single-use + TTL) is
    MODELLED as correct, not measured against Discord.
  - Transport (TLS, Secure/HttpOnly/SameSite cookies, HSTS) and Railway hosting/secret
    posture are out of the model.
  - SECTION 4 superbot read-only API is UNBUILT AND UNROUTED - cannot verify what does
    not exist.

RUN (one command, deterministic, stdlib-only, exit 0 iff all checks + attacks pass):
  python3 sims/intake-002-oauth-trust-gate/oauth_trust_gate_sim.py

MODEL: modelled IdP (Discord) + relying-party (stats site, the reference impl) +
attacker. Seeded random.Random per run for state/code/token generation - REPRODUCIBLE;
production MUST use a CSPRNG (secrets/os.urandom), a disclosed abstraction (see LIMITS).
"""
import base64
import hashlib
import random

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SEEDS = [11, 23, 42, 101, 2027]
REQUIRED_SCOPES = frozenset({"identify", "guilds"})
RL_CAPACITIES = [5, 10, 20]        # rate-limit sweep: token-bucket capacity
RL_REFILLS = [0.5, 1.0, 2.0]       # rate-limit sweep: refill tokens/sec

CLIENT_ID = "stats-site"
CLIENT_SECRET = "modeled-secret"   # NOT a real secret - a model token
REDIRECT_URI = "https://stats.superbot.example/callback"
EVIL_REDIRECT = "https://attacker.example/callback"

CHECKS = {"passed": 0, "failed": 0}


class Reject(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def _b64url(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def _rand_token(rng, n=16):
    # SEEDED pseudo-random for REPRODUCIBILITY. Production MUST use a CSPRNG
    # (secrets.token_urlsafe / os.urandom) - disclosed abstraction (see LIMITS).
    return _b64url(bytes(rng.randrange(256) for _ in range(n)))


class TokenBucket:
    def __init__(self, capacity, refill_per_sec):
        self.capacity = capacity
        self.refill = refill_per_sec
        self.tokens = float(capacity)

    def advance(self, dt):
        self.tokens = min(self.capacity, self.tokens + dt * self.refill)

    def allow(self):
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False


class ModelIdP:
    """Modelled Discord authorization server (authorization-code + PKCE S256)."""

    def __init__(self, rng):
        self.rng = rng
        self.codes = {}     # code -> record; consumed on exchange (single-use)
        self.tokens = {}    # access_token -> {user, scopes}
        self.apps = {
            CLIENT_ID: {"secret": CLIENT_SECRET, "redirects": {REDIRECT_URI}},
        }
        self.users = {
            "victim":   {"g_alpha", "g_beta"},
            "attacker": {"g_evil", "g_beta"},
        }

    def authorize(self, client_id, redirect_uri, scopes, user, code_challenge=None):
        app = self.apps.get(client_id)
        if app is None:
            raise Reject("unknown_client")
        if redirect_uri not in app["redirects"]:        # exact-match allow-list
            raise Reject("redirect_uri_mismatch")
        code = _rand_token(self.rng)
        self.codes[code] = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scopes": frozenset(scopes),
            "user": user,
            "code_challenge": code_challenge,
            "used": False,
        }
        return code

    def token(self, client_id, client_secret, code, redirect_uri,
              code_verifier=None):
        app = self.apps.get(client_id)
        if app is None or app["secret"] != client_secret:
            raise Reject("invalid_client")
        rec = self.codes.get(code)
        if rec is None or rec["used"]:                  # single-use code
            raise Reject("invalid_grant")
        if rec["client_id"] != client_id:
            raise Reject("invalid_grant")
        if rec["redirect_uri"] != redirect_uri:         # must match authorize
            raise Reject("redirect_uri_mismatch")
        if rec["code_challenge"] is not None:           # PKCE binding
            if code_verifier is None:
                raise Reject("pkce_required")
            chal = _b64url(hashlib.sha256(code_verifier.encode()).digest())
            if chal != rec["code_challenge"]:
                raise Reject("pkce_mismatch")
        rec["used"] = True                              # consume
        access_token = _rand_token(self.rng)
        self.tokens[access_token] = {"user": rec["user"], "scopes": rec["scopes"]}
        return {"access_token": access_token, "scopes": rec["scopes"]}

    def userinfo(self, access_token):
        t = self.tokens.get(access_token)
        if t is None:
            raise Reject("invalid_token")
        out = {}
        if "identify" in t["scopes"]:
            out["user_id"] = t["user"]
        if "guilds" in t["scopes"]:
            out["guilds"] = set(self.users[t["user"]])
        return out


class StatsSite:
    """Relying party = the REFERENCE implementation of SECTION 5's six controls."""

    def __init__(self, idp, rng, rl_capacity=10, rl_refill=1.0):
        self.idp = idp
        self.rng = rng
        self.pre = {}       # browser_session -> {state, verifier, used} (server-side)
        self.authed = {}    # authed_session -> {user_id, guild_ids, issued_at}
        self.buckets = {}   # (key, endpoint) -> TokenBucket
        self.rl_capacity = rl_capacity
        self.rl_refill = rl_refill
        self.clock = 0.0

    def login_start(self, browser_session):
        state = _rand_token(self.rng)
        verifier = _rand_token(self.rng, 32)
        challenge = _b64url(hashlib.sha256(verifier.encode()).digest())
        # control 3: state stored SERVER-SIDE, bound to THIS browser session, single-use
        self.pre[browser_session] = {"state": state, "verifier": verifier, "used": False}
        # control 1: scopes are SERVER-AUTHORITATIVE - a client cannot widen them
        return {
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "scope": set(REQUIRED_SCOPES),
            "state": state,
            "code_challenge": challenge,
        }

    def callback(self, browser_session, code, state):
        pre = self.pre.get(browser_session)
        if pre is None:
            raise Reject("no_pending_login")
        if pre["used"]:
            raise Reject("state_replay")
        if state != pre["state"]:                       # CSRF / forged / cross-session
            raise Reject("state_mismatch")
        pre["used"] = True                              # single-use state
        tok = self.idp.token(CLIENT_ID, CLIENT_SECRET, code, REDIRECT_URI,
                             code_verifier=pre["verifier"])
        granted = tok["scopes"]
        # control 1: fail CLOSED if granted scopes are not EXACTLY the minimal request
        if not granted <= REQUIRED_SCOPES or granted != REQUIRED_SCOPES:
            raise Reject("scope_violation")
        info = self.idp.userinfo(tok["access_token"])
        # control 2: DISCARD the access token - store only derived identity
        authed_session = _rand_token(self.rng)
        self.authed[authed_session] = {
            "user_id": info["user_id"],
            "guild_ids": set(info["guilds"]),
            "issued_at": self.clock,
        }
        return authed_session

    def api_stats(self, authed_session, guild_id, spoof_user_id=None):
        sess = self.authed.get(authed_session)
        if sess is None:
            raise Reject("unauthenticated")
        if not self._allow(sess["user_id"], "stats"):   # control 6: rate limit
            raise Reject("rate_limited")
        # control 5: identity is the SESSION's user_id; a client-supplied id is IGNORED
        user_id = sess["user_id"]
        # control 5: cross-server guard - only guilds in the session set are readable
        if guild_id not in sess["guild_ids"]:
            raise Reject("forbidden_guild")
        return {"user_id": user_id, "guild_id": guild_id, "stats": (user_id, guild_id)}

    def _allow(self, key, endpoint):
        b = self.buckets.get((key, endpoint))
        if b is None:
            b = TokenBucket(self.rl_capacity, self.rl_refill)
            self.buckets[(key, endpoint)] = b
        return b.allow()


def honest_login(site, idp, browser, user):
    p = site.login_start(browser)
    code = idp.authorize(p["client_id"], p["redirect_uri"], p["scope"], user,
                         code_challenge=p["code_challenge"])
    return site.callback(browser, code, p["state"])


def expect_reject(label, fn, code=None):
    try:
        fn()
    except Reject as e:
        if code is not None and e.code != code:
            raise AssertionError("%s: expected reject '%s', got '%s'" % (label, code, e.code))
        CHECKS["passed"] += 1
        return (label, "DEFEATED", "reject:" + e.code)
    raise AssertionError("%s: expected reject but the call SUCCEEDED (hole!)" % label)


def expect_ok(label, fn):
    res = fn()
    CHECKS["passed"] += 1
    return (label, "PASS", str(res))


def run_attacks(seed, rl_capacity=10, rl_refill=1.0):
    log = []
    rng = random.Random(seed)
    idp = ModelIdP(rng)
    site = StatsSite(idp, rng, rl_capacity, rl_refill)

    # sanity: an honest login yields a working session
    vs = honest_login(site, idp, "vb", "victim")
    log.append(expect_ok("honest-login", lambda: site.api_stats(vs, "g_alpha")))

    # --- SECTION 5 item 1: scope minimalism ---
    pchk = site.login_start("scope-check")
    assert set(pchk["scope"]) == set(REQUIRED_SCOPES), "site requested non-minimal scopes"
    CHECKS["passed"] += 1
    log.append(("scope-request-minimal", "PASS", str(sorted(pchk["scope"]))))
    # fail CLOSED if the IdP returns an OVER-SCOPED grant (malicious/misconfig IdP)
    b5 = "vb5"; p5 = site.login_start(b5)
    over_code = idp.authorize(CLIENT_ID, REDIRECT_URI, {"identify", "guilds", "email"},
                              "victim", code_challenge=p5["code_challenge"])
    log.append(expect_reject("scope-upgrade-failclosed",
                             lambda: site.callback(b5, over_code, p5["state"]), "scope_violation"))
    # redirect_uri exact-match allow-list (open-redirect / code-exfil defense)
    log.append(expect_reject("redirect-uri-tamper",
                             lambda: idp.authorize(CLIENT_ID, EVIL_REDIRECT, REQUIRED_SCOPES, "victim"),
                             "redirect_uri_mismatch"))

    # --- SECTION 5 item 3: CSRF / state correctness ---
    b2 = "vb2"; p2 = site.login_start(b2)
    code2 = idp.authorize(CLIENT_ID, REDIRECT_URI, p2["scope"], "victim",
                          code_challenge=p2["code_challenge"])
    log.append(expect_reject("csrf-forged-state",
                             lambda: site.callback(b2, code2, "not-the-state"), "state_mismatch"))
    # forged attempt did NOT consume state -> the honest retry still works
    log.append(expect_ok("csrf-honest-after-forge",
                          lambda: site.callback(b2, code2, p2["state"])))
    # state replay: reuse a consumed state -> single-use store rejects
    log.append(expect_reject("state-replay",
                             lambda: site.callback(b2, code2, p2["state"]), "state_replay"))
    # login-CSRF / session fixation: attacker's code+state completed in victim's browser
    ab = "attacker-browser"; pa = site.login_start(ab)
    code_a = idp.authorize(CLIENT_ID, REDIRECT_URI, pa["scope"], "attacker",
                           code_challenge=pa["code_challenge"])
    b3 = "victim-fresh"; site.login_start(b3)   # victim starts their OWN login
    log.append(expect_reject("login-csrf-fixation",
                             lambda: site.callback(b3, code_a, pa["state"]), "state_mismatch"))

    # --- SECTION 5 item 4: code replay / injection ---
    b4 = "vb4"; p4 = site.login_start(b4)
    code4 = idp.authorize(CLIENT_ID, REDIRECT_URI, p4["scope"], "victim",
                          code_challenge=p4["code_challenge"])
    site.callback(b4, code4, p4["state"])       # first exchange consumes the code
    b4b = "vb4b"; p4b = site.login_start(b4b)
    log.append(expect_reject("code-replay",
                             lambda: site.callback(b4b, code4, p4b["state"]), None))
    # PKCE binding: a code bound to challenge X rejects a wrong verifier (defense-in-depth)
    vgood = _rand_token(rng, 32)
    chal = _b64url(hashlib.sha256(vgood.encode()).digest())
    code_p = idp.authorize(CLIENT_ID, REDIRECT_URI, REQUIRED_SCOPES, "victim", code_challenge=chal)
    log.append(expect_reject("pkce-wrong-verifier",
                             lambda: idp.token(CLIENT_ID, CLIENT_SECRET, code_p, REDIRECT_URI,
                                               code_verifier="wrong-verifier"), "pkce_mismatch"))

    # --- SECTION 5 item 2: token lifecycle (no long-lived token storage) ---
    b6 = "vb6"; s6 = honest_login(site, idp, b6, "victim")
    sess = site.authed[s6]
    assert set(sess.keys()) == {"user_id", "guild_ids", "issued_at"}, "session holds unexpected fields"
    assert "access_token" not in sess and "refresh_token" not in sess, "token stored in session!"
    dumped = repr(site.authed)
    for at in idp.tokens:                       # 'dump the session store' -> no creds
        assert at not in dumped, "an access token leaked into the site session store"
    CHECKS["passed"] += 1
    log.append(("token-lifecycle-no-storage", "PASS", str(sorted(sess.keys()))))

    # --- SECTION 5 item 5: per-user data isolation ---
    sA = honest_login(site, idp, "attacker-real", "attacker")
    r = site.api_stats(sA, "g_beta", spoof_user_id="victim")   # both share g_beta
    assert r["user_id"] == "attacker", "IDOR: spoofed user_id honored!"
    CHECKS["passed"] += 1
    log.append(("idor-user-id-spoof", "DEFEATED", r["user_id"]))
    log.append(expect_reject("cross-server-guild",
                             lambda: site.api_stats(sA, "g_alpha"), "forbidden_guild"))

    # --- SECTION 5 item 6: rate limiting ---
    sR = honest_login(site, idp, "rl-victim", "victim")
    site.buckets.clear()
    allowed = 0
    for _ in range(rl_capacity + 10):
        try:
            site.api_stats(sR, "g_alpha")
            allowed += 1
        except Reject as e:
            assert e.code == "rate_limited", "unexpected reject in burst: " + e.code
    assert allowed == rl_capacity, "burst not bounded to capacity: %d != %d" % (allowed, rl_capacity)
    CHECKS["passed"] += 1
    log.append(("rate-limit-burst-bound", "DEFEATED", "allowed=%d cap=%d" % (allowed, rl_capacity)))
    for b in site.buckets.values():
        b.advance(2.0 / rl_refill)              # refill ~2 tokens over virtual time
    site.api_stats(sR, "g_alpha")               # a token returned -> passes again
    CHECKS["passed"] += 1
    log.append(("rate-limit-refill", "PASS", "refilled"))

    # --- HOLE 2: `guilds` over-read (fresh victim still holds 2 guilds) ---
    sO = honest_login(site, idp, "over-victim", "victim")
    over = site.authed[sO]["guild_ids"]
    assert len(over) >= 2, "expected the over-read to expose multiple guilds"
    CHECKS["passed"] += 1
    log.append(("HOLE-guilds-over-read", "PLAUSIBLE-HOLE",
                "identify+guilds returns the user's FULL guild list (%d here); only the "
                "viewed server is needed -> privacy over-collection, minimise/don't retain" % len(over)))

    # --- HOLE 1: stale guild membership (session caches the guild set at login) ---
    sH = honest_login(site, idp, "stale-victim", "victim")
    idp.users["victim"].discard("g_alpha")      # membership changes AFTER login
    site.buckets.clear()
    still = None
    try:
        site.api_stats(sH, "g_alpha")
        still = True
    except Reject:
        still = False
    assert still is True, "expected the stale-membership hole to reproduce"
    CHECKS["passed"] += 1
    log.append(("HOLE-stale-guild-membership", "PLAUSIBLE-HOLE",
                "cached session read a server the user has LEFT -> needs per-request "
                "membership re-check or a short session TTL"))
    return log


def summarize(log):
    return tuple((name, status) for (name, status, _v) in log)


JUDGMENT_ONLY = [
    ("live Discord IdP enforcement",
     "redirect_uri exact-match + code single-use + code TTL are MODELLED as correct; "
     "verify empirically against the real Discord app config at launch."),
    ("transport / cookies",
     "the state defense is void over plaintext; assert HSTS + Secure/HttpOnly/SameSite "
     "cookies + TLS-only in live response headers (not exercisable here)."),
    ("Railway hosting / secret posture",
     "the 3 live websites-lane services' auth posture was never inspected; confirm the "
     "Discord client_secret lives in a secret store (not env dump / not repo) + env isolation."),
    ("pre-auth rate-limit keying",
     "/login/start limiting must key on IP/fingerprint and survive rotation "
     "(proof-of-work/captcha at scale) - not modelled here."),
    ("SECTION 4 superbot read-only API",
     "UNBUILT AND UNROUTED - cannot verify what does not exist; needs its own superbot-lane "
     "ORDER + its own trust verification (DB-side per-user isolation, token scoping)."),
]


def print_report(log):
    items = [
        ("1 scope-minimalism", ["scope-request-minimal", "scope-upgrade-failclosed", "redirect-uri-tamper"]),
        ("2 token-lifecycle",  ["token-lifecycle-no-storage"]),
        ("3 csrf-state",       ["csrf-forged-state", "csrf-honest-after-forge", "state-replay", "login-csrf-fixation"]),
        ("4 code-replay/inj",  ["code-replay", "pkce-wrong-verifier"]),
        ("5 per-user-isolation", ["idor-user-id-spoof", "cross-server-guild"]),
        ("6 rate-limiting",    ["rate-limit-burst-bound", "rate-limit-refill"]),
    ]
    by = {name: (status, v) for (name, status, v) in log}
    print("=== SECTION 5 OAuth trust-gate - executed adversarial suite (canonical seed %d) ===" % SEEDS[0])
    for item, names in items:
        print("  S5.%s -> PASS (all listed attacks defeated / properties hold)" % item)
        for n in names:
            if n in by:
                print("        %-28s %-10s %s" % (n, by[n][0], by[n][1]))
    print("  --- surfaced HOLES (named changes required) ---")
    for (name, status, v) in log:
        if name.startswith("HOLE"):
            print("        %-28s %-14s %s" % (name, status, v))
    print("  --- JUDGMENT-ONLY (NOT EXECUTED - hypotheses for launch-time live tests) ---")
    for (name, note) in JUDGMENT_ONLY:
        print("        %-32s %s" % (name, note))


def main():
    # multi-seed stability: the qualitative outcome must be identical across seeds
    base = summarize(run_attacks(SEEDS[0]))
    for s in SEEDS[1:]:
        assert summarize(run_attacks(s)) == base, "seed %d diverged qualitatively" % s
        CHECKS["passed"] += 1

    # rate-limit robustness sweep: burst always bounded to capacity across the grid
    for cap in RL_CAPACITIES:
        for rf in RL_REFILLS:
            log = run_attacks(SEEDS[0], cap, rf)
            rec = [x for x in log if x[0] == "rate-limit-burst-bound"][0]
            assert ("cap=%d" % cap) in rec[2] and ("allowed=%d" % cap) in rec[2], \
                "rate-limit sweep cap=%d refill=%s not bounded" % (cap, rf)
            CHECKS["passed"] += 1

    print_report(run_attacks(SEEDS[0]))
    print("\nSEEDS: %s (qualitatively identical)  RATE-LIMIT SWEEP: %dx%d grid, all bounded"
          % (SEEDS, len(RL_CAPACITIES), len(RL_REFILLS)))
    print("SELF-CHECKS: %d passed, %d failed" % (CHECKS["passed"], CHECKS["failed"]))
    assert CHECKS["failed"] == 0


if __name__ == "__main__":
    main()
