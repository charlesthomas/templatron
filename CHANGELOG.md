# CHANGELOG



## v0.4.4 (2024-02-19)

### Ci

* ci: add linting with black and testing with pytest ([`4aa79aa`](https://github.com/charlesthomas/templatron/commit/4aa79aa14c1e49472ca231424a97a2d4793e74d2))


## v0.4.3 (2024-02-19)

### Fix

* fix: ok may this&#39;ll do it ([`bb05fa0`](https://github.com/charlesthomas/templatron/commit/bb05fa0759f50752f68d41a059fb634311949311))


## v0.4.2 (2024-02-19)

### Fix

* fix: try on push tags instead ([`dcb3fe2`](https://github.com/charlesthomas/templatron/commit/dcb3fe243ba1cb4aa2c3b8e60417741e2e988701))


## v0.4.1 (2024-02-19)

### Fix

* fix: image tags ([`ed9264f`](https://github.com/charlesthomas/templatron/commit/ed9264f511687b2ba244434fa0139f9615662fc0))


## v0.4.0 (2024-02-19)

### Feature

* feat: add image ([`e2b4b2d`](https://github.com/charlesthomas/templatron/commit/e2b4b2dd8fe24c5e4d496b67bbdc5a9b7319ee64))

### Fix

* fix: update command ([`09051a0`](https://github.com/charlesthomas/templatron/commit/09051a08ac79eb943be2a0209210a929914d9800))


## v0.3.5 (2024-02-18)

### Chore

* chore: ran black ([`9c7cb85`](https://github.com/charlesthomas/templatron/commit/9c7cb85e496a1bfbdeb602bef2ca8842c34603f0))


## v0.3.4 (2024-02-18)

### Ci

* ci: add pytest ([`f18183b`](https://github.com/charlesthomas/templatron/commit/f18183b574ad5dcb5f0d11256390639f7c3adbb3))

* ci: add black ([`1c3af1f`](https://github.com/charlesthomas/templatron/commit/1c3af1f7a4c1d66c3078abe2573c07964d70d654))

### Test

* test: get tests passing again (mostly)

there&#39;s a warning that appears to be coming from
inside the `GitHub` module, and
two tests had to be commented out entirely due to
what i think is a bug in `sh` ([`523d7dd`](https://github.com/charlesthomas/templatron/commit/523d7dd089fc62713d57c0da262bbf2d7f075b74))


## v0.3.3 (2024-02-17)

### Chore

* chore: egg-info in gitignore ([`9bbb318`](https://github.com/charlesthomas/templatron/commit/9bbb318222ed52a737865b97b644542df514f793))

### Ci

* ci: testing misconfiguration fix ([`a4a4447`](https://github.com/charlesthomas/templatron/commit/a4a444721042ddf8ceeb9c7d0c1e95e92abddb1a))

### Fix

* fix: ci cleanup ([`0c58951`](https://github.com/charlesthomas/templatron/commit/0c589513e871a5f315446020371e9b023c1ed2b8))


## v0.3.2 (2024-02-15)

### Chore

* chore(deps-dev): bump python-semantic-release from 8.7.0 to 9.1.0

Bumps [python-semantic-release](https://github.com/python-semantic-release/python-semantic-release) from 8.7.0 to 9.1.0.
- [Release notes](https://github.com/python-semantic-release/python-semantic-release/releases)
- [Changelog](https://github.com/python-semantic-release/python-semantic-release/blob/master/CHANGELOG.md)
- [Commits](https://github.com/python-semantic-release/python-semantic-release/compare/v8.7.0...v9.1.0)

---
updated-dependencies:
- dependency-name: python-semantic-release
  dependency-type: direct:development
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt; ([`2319350`](https://github.com/charlesthomas/templatron/commit/231935089b79c0264a2b9dd464ca65675f66f5d4))


## v0.3.1 (2024-02-15)

### Chore

* chore(deps): bump pygithub from 2.1.1 to 2.2.0

Bumps [pygithub](https://github.com/pygithub/pygithub) from 2.1.1 to 2.2.0.
- [Release notes](https://github.com/pygithub/pygithub/releases)
- [Changelog](https://github.com/PyGithub/PyGithub/blob/main/doc/changes.rst)
- [Commits](https://github.com/pygithub/pygithub/compare/v2.1.1...v2.2.0)

---
updated-dependencies:
- dependency-name: pygithub
  dependency-type: direct:production
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt; ([`bb2c29b`](https://github.com/charlesthomas/templatron/commit/bb2c29bbdb59fb3a8c687d45c7ab26d622541844))


## v0.3.0 (2024-01-27)

### Chore

* chore: assume user first

try user, fail to org; rather than the other way around ([`3565e9f`](https://github.com/charlesthomas/templatron/commit/3565e9ff299fcb5b77d9ca77df0423403f3710e4))

### Feature

* feat: stop defaulting `--autoclean` ([`843463a`](https://github.com/charlesthomas/templatron/commit/843463aed66b3a78a6f6ec1732f0e047de5e280c))

### Unknown

* doc: fix README ([`bb0ff6b`](https://github.com/charlesthomas/templatron/commit/bb0ff6be678af8484c1d4af9dd6faf4cdeebc339))


## v0.2.7 (2024-01-27)

### Chore

* chore(ci): Create dependabot.yml ([`24d79c4`](https://github.com/charlesthomas/templatron/commit/24d79c43f60c9ee023b5204e2a6731d85c7096ea))


## v0.2.6 (2024-01-27)

### Fix

* fix(build): try to make a GitHub Release myself ([`263a5e5`](https://github.com/charlesthomas/templatron/commit/263a5e5b14b9eb40ba864a0768f66cf2861f46a5))


## v0.2.5 (2024-01-27)

### Fix

* fix(ci): try to disable vcs release in github actions ([`b2877ac`](https://github.com/charlesthomas/templatron/commit/b2877ac0aee077f4c9a88574833f1f8c3c13c43f))


## v0.2.4 (2024-01-27)

### Fix

* fix(build): disable GH Releases

[pending bug fix](https://github.com/python-semantic-release/python-semantic-release/issues/818) ([`0fcd3cd`](https://github.com/charlesthomas/templatron/commit/0fcd3cdf98bade3537e2237ba44716f2aeb792f6))


## v0.2.3 (2024-01-27)

### Fix

* fix: re-add __version__ for `templatron --version` option ([`086cf62`](https://github.com/charlesthomas/templatron/commit/086cf62bfaab8ba3465d74679b4808bf97615662))


## v0.2.2 (2024-01-27)

### Fix

* fix: misc

- add 🤖 emoji to name in commit template
- shorten SHA in branch names
- change default branch separator from `/` to `-` b/c `/` is dumb and bad ([`bead75f`](https://github.com/charlesthomas/templatron/commit/bead75fe30b8d84708de15f9d1037e6b9cb6ec57))

### Unknown

* Poetry (#13)

* fix: leave munge_answers out, but add pretty printing back

* feat(ci): migrate to poetry

* build: add python-semantic-release

* feat(ci): add automatic semantic versioning via GitHub Actions ([`1e4973f`](https://github.com/charlesthomas/templatron/commit/1e4973f27ac332de803a6e4c0db34536565f5d0c))


## v0.2.1 (2024-01-23)

### Fix

* fix: lol oops ([`68ba533`](https://github.com/charlesthomas/templatron/commit/68ba5337cad5f6a6eb175c0cf8163f7faae514ae))


## v0.2.0 (2024-01-22)

### Feature

* feat: rebrand

filesync -&gt; templatron ([`63a9114`](https://github.com/charlesthomas/templatron/commit/63a9114447d66a72bf4b6ddc2c6fdf18c41051aa))

### Unknown

* Update dependencies (#8)

* chore: update requirements.txt

i suspect this is gonna break copier imports pretty badly, since we&#39;re
going from 5.x to 8.x

* feat: install as `tt` in addition to `templatron`

* fix: `copier.copy` became `copier.run_copy` between 5.x and 9.x

* fix!: force is no longer supported

* wip: use get_user instead of get_organization

THIS IS A BREAKING-CHANGE AS-IS!

need to add a new config option defaulted to `org` that switches the API
calls between `get_organization` and `get_user`

* doc: add info on previously undocumented config options

* fix: try to `get_organization` and if it 404s, use `get_user` instead

* fix: final touches to make templatron work with up-to-date depencies

* version 0.2.0 ([`e8f30b4`](https://github.com/charlesthomas/templatron/commit/e8f30b4a5750df0dde6b08850cb47b007f83b5e5))

* doc(fix): Why was there a blank example? ([`c91bf30`](https://github.com/charlesthomas/templatron/commit/c91bf300f783170aa237d152d1c80b4accb3612b))

* doc: update NOTICE

initial fork commit included mezmo/filesync commit in the NOTICE
this commit adds that initial templatron commit into the NOTICE ([`81c2fc2`](https://github.com/charlesthomas/templatron/commit/81c2fc29d1e12c78b7e8dcf24853814d3f5765eb))

* fork mezmo/filesync@8db3574aaa5465fb693d24443d971e0284f22e26 ([`6387520`](https://github.com/charlesthomas/templatron/commit/63875208270478041174660e4bd8ed1bc0e483dd))

* Initial commit ([`a6be404`](https://github.com/charlesthomas/templatron/commit/a6be404a80918fd3603e343e9d3dfa2c38725f64))
