# CHANGELOG



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
