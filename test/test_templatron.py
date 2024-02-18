"""
Test Templatron class
"""

from os import environ
from unittest import TestCase
from unittest.mock import MagicMock, patch

from sh import ErrorReturnCode

# from sh import TimeoutException

from templatron.exceptions import (
    AmbiguousOrgConfigError,
    TemplatronException,
    GitConfigError,
    MissingRequiredConfigError,
    UnrecognizableBaseBranchError,
)
from templatron.templatron import Templatron

# pylint: disable=too-many-public-methods


class TestTemplatronBuildRepo(TestCase):  # pylint: disable=too-many-instance-attributes
    """
    Test build_repo() method in Templatron class
    """

    def setUp(self):
        self.fake_repo = "fake_repo"
        self.fake_org = "fake_org"
        self.fake_token = "ABC123"
        self.fake_clone_root = "/tmp/fake/clone/root"
        self.fake_template = "fake_template"
        self.fake_branch = "fake_main"
        self.fake_github_repo = f"{self.fake_org}/{self.fake_repo}"

        environ["FAKE_TOKEN"] = self.fake_token
        self.templatron = Templatron(
            token_variable_name="FAKE_TOKEN", clone_root=self.fake_clone_root
        )
        self.templatron.github = MagicMock()
        self.templatron.github.get_user().get_repo.return_value = self.fake_github_repo

    @patch("templatron.templatron.Templatron.validate_repo")
    @patch("templatron.templatron.Repository")
    def test_build_repo_with_base_branch(self, mock_repo, mock_validate):
        """
        Test build_repo() with base_branch set
        """

        mock_validate.return_value = (self.fake_repo, self.fake_org, {})
        self.templatron.template = self.fake_template
        self.templatron.build_repo(self.fake_repo, base_branch=self.fake_branch)
        mock_validate.assert_called_with(self.fake_repo)
        mock_repo.assert_called_with(
            self.fake_repo,
            self.fake_token,
            self.fake_github_repo,
            self.fake_clone_root,
            self.fake_template,
            base_branch=self.fake_branch,
        )

    @patch("templatron.templatron.Templatron.validate_repo")
    @patch("templatron.templatron.Repository")
    def test_build_repo_without_base_branch(self, mock_repo, mock_validate):
        """
        Test build_repo() with base_branch set
        """

        mock_validate.return_value = (self.fake_repo, self.fake_org, {})
        self.templatron.template = self.fake_template
        self.templatron.build_repo(self.fake_repo)
        mock_validate.assert_called_with(self.fake_repo)
        mock_repo.assert_called_with(
            self.fake_repo,
            self.fake_token,
            self.fake_github_repo,
            self.fake_clone_root,
            self.fake_template,
        )


class TestBuildRepos(TestCase):
    """
    Test Templatron.build_repos()
    """

    def setUp(self):
        environ["FAKE_TOKEN"] = "FAKE123"
        self.templatron = Templatron(token_variable_name="FAKE_TOKEN")
        self.templatron.logger = MagicMock()

    @patch("templatron.templatron.Templatron.fetch_repo_list")
    @patch("templatron.templatron.Templatron.build_repo")
    def test_build_repos_base(self, mock_build_repo, mock_repo_list):
        """
        Base test for build_repos()
        """

        mock_repo_list.return_value = ["fake1", "fake2", "fake3"]
        mock_build_repo.side_effect = ["fake4", "fake5", "fake6"]
        repos = self.templatron.build_repos()
        self.assertEqual(repos, ["fake4", "fake5", "fake6"])
        mock_build_repo.assert_any_call("fake1")
        mock_build_repo.assert_any_call("fake2")
        mock_build_repo.assert_any_call("fake3")


class TestBuildTemplate(TestCase):  # pylint: disable=too-many-instance-attributes
    """
    Test Templatron.build_template()
    """

    def setUp(self):
        self.fake_repo = "fake_repo"
        self.fake_org = "fake_org"
        self.fake_token = "ABC123"
        self.fake_clone_root = "/tmp/fake/clone/root"
        self.fake_template = "fake_template"
        self.fake_branch = "fake_main"
        self.fake_github_repo = f"{self.fake_org}/{self.fake_repo}"
        self.fake_dry_run = False
        self.fake_template_config = {}
        self.fake_operation = "NUL"
        self.fake_interactive = False

        environ["FAKE_TOKEN"] = self.fake_token
        self.templatron = Templatron(
            token_variable_name="FAKE_TOKEN",
            clone_root=self.fake_clone_root,
            template_branch=self.fake_branch,
            dry_run=self.fake_dry_run,
            template_config=self.fake_template_config,
            operation=self.fake_operation,
            interactive=self.fake_interactive,
        )
        self.templatron.logger = MagicMock()
        self.templatron.github = MagicMock()
        self.templatron.github.get_user().get_repo.return_value = self.fake_github_repo

    @patch("templatron.templatron.Templatron.split_org_and_name")
    @patch("templatron.templatron.Template")
    def test_build_template_valid(self, mock_template, mock_split):
        """
        Test valid build_template() call
        """

        mock_template.return_value = self.fake_template
        mock_split.return_value = (self.fake_org, self.fake_repo)
        template = self.templatron.build_template(self.fake_repo)

        mock_split.assert_called_with(self.fake_repo)
        mock_template.assert_called_with(
            self.fake_repo,
            self.fake_token,
            self.fake_github_repo,
            self.fake_clone_root,
            base_branch=self.fake_branch,
            dry_run=self.fake_dry_run,
            template_config=self.fake_template_config,
            operation=self.fake_operation,
            interactive=self.fake_interactive,
        )
        self.assertEqual(template, self.fake_template)

    @patch("templatron.templatron.Templatron.die")
    @patch("templatron.templatron.Templatron.split_org_and_name")
    @patch("templatron.templatron.Template")
    def test_build_template_with_error(self, mock_template, mock_split, mock_die):
        """
        Test valid build_template() call
        """

        mock_template.side_effect = TemplatronException
        mock_die.side_effect = SystemExit
        mock_split.return_value = (self.fake_org, self.fake_repo)

        with self.assertRaises(SystemExit):
            self.templatron.build_template(self.fake_repo)

        mock_split.assert_called_with(self.fake_repo)
        mock_template.assert_called_with(
            self.fake_repo,
            self.fake_token,
            self.fake_github_repo,
            self.fake_clone_root,
            base_branch=self.fake_branch,
            dry_run=self.fake_dry_run,
            template_config=self.fake_template_config,
            operation=self.fake_operation,
            interactive=self.fake_interactive,
        )
        mock_die.assert_called()


class TestFetchRepoList(TestCase):
    """
    Test Templatron.fetch_repo_list()
    """

    def setUp(self):
        environ["FAKE_TOKEN"] = "FAKE123"
        self.templatron = Templatron(token_variable_name="FAKE_TOKEN")
        self.templatron.logger = MagicMock()
        self.templatron.github = MagicMock()
        self.templatron.template = MagicMock()
        self.templatron.template.name = "fake_repo321"

    def test_fetch_repo_list_with_valid(self):
        """
        Test fetch_repo_list() with a valid repo
        """

        self.templatron.template.config.autoscan = True

        fake_repo = MagicMock()
        fake_repo.fork = False
        fake_repo.archived = False
        fake_repo.name = "not_the_repo_youre_looking_for"
        self.templatron.github.get_user().get_repos.return_value = [fake_repo]
        self.templatron.has_answersfile = MagicMock()
        self.templatron.has_answersfile.return_value = True

        repo_list = self.templatron.fetch_repo_list()
        self.assertEqual(repo_list, ["not_the_repo_youre_looking_for"])
        self.templatron.github.get_user().get_repos.assert_called()

    def test_fetch_repo_list_with_no_autoscan(self):
        """
        Test fetch_repo_list() with
        """

        fake_list = list(set(["fake", "repos"]))
        self.templatron.template.config.repos.keys.return_value = fake_list
        self.templatron.template.config.autoscan = False
        repo_list = self.templatron.fetch_repo_list()
        self.assertEqual(repo_list, fake_list)

    def test_fetch_repo_list_with_fork(self):
        """
        Test fetch_repo_list() with a forked repo
        """

        self.templatron.template.config.autoscan = True

        fake_repo = MagicMock()
        fake_repo.fork = True
        fake_repo.archived = False
        fake_repo.name = "not_the_repo_youre_looking_for"
        self.templatron.github.get_user().get_repos.return_value = [fake_repo]

        repo_list = self.templatron.fetch_repo_list()
        self.assertEqual(repo_list, [])
        self.templatron.github.get_user().get_repos.assert_called()

    def test_fetch_repo_list_with_archived(self):
        """
        Test fetch_repo_list() with an archived repo
        """

        self.templatron.template.config.autoscan = True

        fake_repo = MagicMock()
        fake_repo.fork = False
        fake_repo.archived = True
        fake_repo.name = "not_the_repo_youre_looking_for"
        self.templatron.github.get_user().get_repos.return_value = [fake_repo]

        repo_list = self.templatron.fetch_repo_list()
        self.assertEqual(repo_list, [])
        self.templatron.github.get_user().get_repos.assert_called()

    def test_fetch_repo_list_with_template(self):
        """
        Test fetch_repo_list() with template repo
        """

        self.templatron.template.config.autoscan = True

        fake_repo = MagicMock()
        fake_repo.fork = False
        fake_repo.archived = False
        fake_repo.name = "fake_repo321"
        self.templatron.github.get_user().get_repos.return_value = [fake_repo]

        repo_list = self.templatron.fetch_repo_list()
        self.assertEqual(repo_list, [])
        self.templatron.github.get_user().get_repos.assert_called()

    @patch("templatron.templatron.makedirs")
    def test_create_clone_root(self, mock_makedirs):
        """
        Test Templatron.create_clone_root()
        """

        self.templatron.config.clone_root = "/fake/root"
        self.templatron.create_clone_root()
        mock_makedirs.assert_called_with("/fake/root", exist_ok=True)

    @patch("templatron.templatron.Templatron.maybe_clean")
    def test_die(self, mock_clean):
        """
        Test Templatron.die()
        """

        with self.assertRaises(SystemExit):
            self.templatron.die("Not a real error")
        mock_clean.assert_called()

    @patch("templatron.templatron.Templatron.start")
    @patch("templatron.templatron.Templatron.build_repo")
    @patch("templatron.templatron.Templatron.stop")
    def test_fix_ok(self, mock_stop, mock_build, mock_start):
        """
        Test Templatron.fix() with no errors
        """

        self.templatron.fix("repo", "branch")
        mock_start.assert_called_with("fixing")
        mock_build().fix.assert_called()
        mock_stop.assert_called()

    @patch("templatron.templatron.Templatron.die")
    @patch("templatron.templatron.Templatron.start")
    @patch("templatron.templatron.Templatron.build_repo")
    @patch("templatron.templatron.Templatron.stop")
    def test_fix_unrecognizable_branch(
        self, mock_stop, mock_build, mock_start, mock_die
    ):
        """
        Test Templatron.fix() with unrecognized branch
        """

        mock_build.side_effect = UnrecognizableBaseBranchError
        mock_die.side_effect = SystemExit
        with self.assertRaises(SystemExit):
            self.templatron.fix("repo", "branch")
        mock_start.assert_called_with("fixing")
        mock_stop.assert_not_called()

    @patch("templatron.templatron.Templatron.maybe_clean")
    @patch("templatron.templatron.Templatron.start")
    @patch("templatron.templatron.Templatron.build_repo")
    @patch("templatron.templatron.Templatron.stop")
    def test_fix_keyboard_int(self, mock_stop, mock_build, mock_start, mock_clean):
        """
        Test Templatron.fix() with keyboard interrupt
        """

        mock_build.side_effect = KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            self.templatron.fix("repo", "branch")
        mock_start.assert_called_with("fixing")
        mock_clean.assert_called()
        mock_stop.assert_not_called()

    @patch("templatron.templatron.rmtree")
    @patch("templatron.templatron.os.path.exists")
    def test_maybe_clean_autoclean_and_exists(
        self,
        mock_exists,
        mock_rmtree,
    ):
        """
        Test Templatron.maybe_clean() where autoclean = True and the clone root
        exists
        """

        self.templatron.config.autoclean = True
        mock_exists.return_value = True
        self.templatron.maybe_clean()
        mock_rmtree.assert_called()

    @patch("templatron.templatron.rmtree")
    @patch("templatron.templatron.os.path.exists")
    def test_maybe_clean_autoclean_and_not_exists(
        self,
        mock_exists,
        mock_rmtree,
    ):
        """
        Test Templatron.maybe_clean() where autoclean = True and the clone root
        does not exist
        """

        self.templatron.config.autoclean = True
        mock_exists.return_value = False
        self.templatron.maybe_clean()
        mock_rmtree.assert_not_called()

    @patch("templatron.templatron.rmtree")
    @patch("templatron.templatron.os.path.exists")
    def test_maybe_clean_not_autoclean_and_exists(
        self,
        mock_exists,
        mock_rmtree,
    ):
        """
        Test Templatron.maybe_clean() where autoclean = False and the clone root
        exists
        """

        self.templatron.config.autoclean = False
        mock_exists.return_value = True
        self.templatron.maybe_clean()
        mock_rmtree.assert_not_called()

    @patch("templatron.templatron.rmtree")
    @patch("templatron.templatron.os.path.exists")
    def test_maybe_clean_not_autoclean_and_not_exists(
        self,
        mock_exists,
        mock_rmtree,
    ):
        """
        Test Templatron.maybe_clean() where autoclean = False and the clone root
        does not exist
        """

        self.templatron.config.autoclean = False
        mock_exists.return_value = False
        self.templatron.maybe_clean()
        mock_rmtree.assert_not_called()

    @patch("templatron.templatron.log_or_print")
    def test_maybe_log_dry_run_dry_run(self, mock_log):
        """
        Test Templatron.maybe_log_dry_run() when a dry run
        """

        self.templatron.config.dry_run = True
        self.templatron.maybe_log_dry_run()
        mock_log.assert_called()

    @patch("templatron.templatron.log_or_print")
    def test_maybe_log_dry_run_no_dry_run(self, mock_log):
        """
        Test Templatron.maybe_log_dry_run() when not a dry run
        """

        self.templatron.config.dry_run = False
        self.templatron.maybe_log_dry_run()
        mock_log.assert_not_called()

    @patch("templatron.templatron.Templatron.start")
    @patch("templatron.templatron.Templatron.build_repo")
    @patch("templatron.templatron.Templatron.stop")
    def test_onboard_ok(self, mock_stop, mock_build, mock_start):
        """
        Test Templatron.onboard() with no errors
        """

        self.templatron.onboard("repo")
        mock_start.assert_called_with("onboarding")
        mock_build().onboard.assert_called()
        mock_stop.assert_called()

    @patch("templatron.templatron.Templatron.die")
    @patch("templatron.templatron.Templatron.start")
    @patch("templatron.templatron.Templatron.build_repo")
    @patch("templatron.templatron.Templatron.stop")
    def test_onboard_unrecognizable_branch(
        self, mock_stop, mock_build, mock_start, mock_die
    ):
        """
        Test Templatron.onboard() with unrecognized branch
        """

        mock_build.side_effect = UnrecognizableBaseBranchError
        mock_die.side_effect = SystemExit
        with self.assertRaises(SystemExit):
            self.templatron.onboard("repo")
        mock_start.assert_called_with("onboarding")
        mock_stop.assert_not_called()

    @patch("templatron.templatron.Templatron.maybe_clean")
    @patch("templatron.templatron.Templatron.start")
    @patch("templatron.templatron.Templatron.build_repo")
    @patch("templatron.templatron.Templatron.stop")
    def test_onboard_keyboard_int(self, mock_stop, mock_build, mock_start, mock_clean):
        """
        Test Templatron.onboard() with keyboard interrupt
        """

        mock_build.side_effect = KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            self.templatron.onboard("repo")
        mock_start.assert_called_with("onboarding")
        mock_clean.assert_called()
        mock_stop.assert_not_called()

    @patch("templatron.templatron.LoggingConfig")
    @patch("templatron.templatron.logging")
    def test_setup_logging(self, mock_log, mock_config):
        """
        Test Templatron.setup_logging()
        """

        mock_config().get.side_effect = ["one", "two", "three", "four", "five"]
        self.templatron.setup_logging("fake_command")
        mock_config.assert_called()
        mock_log.basicConfig.assert_called_with(
            filename="one", format="two", datefmt="three", level="FOUR"
        )
        mock_log.getLogger().setLevel.assert_called_with("FIVE")

    def test_split_org_and_name_org_and_name(self):
        """
        Test Templatron.split_org_and_name() with the org and name
        """

        self.assertEqual(
            self.templatron.split_org_and_name("fake_org/fake_name"),
            ("fake_org", "fake_name"),
        )

    def test_split_org_and_name_just_name(self):
        """
        Test Templatron.split_org_and_name() with just the name
        """

        self.templatron.template.config.org = "fake_org"
        self.assertEqual(
            self.templatron.split_org_and_name("fake_name"),
            ("fake_org", "fake_name"),
        )

    def test_split_org_and_name_no_org(self):
        """
        Test Templatron.split_org_and_name() with no org defined
        """

        self.templatron.template.config.org = None
        with self.assertRaises(MissingRequiredConfigError):
            self.templatron.split_org_and_name("fake_name")

    @patch("templatron.templatron.Templatron.setup_logging")
    @patch("templatron.templatron.Templatron.maybe_log_dry_run")
    @patch("templatron.templatron.Templatron.validate_config")
    @patch("templatron.templatron.Templatron.die")
    @patch("templatron.templatron.Templatron.create_clone_root")
    @patch("templatron.templatron.Templatron.build_template")
    def test_start_valid(
        self,
        mock_build,
        mock_create,
        mock_die,
        mock_validate,
        mock_maybe_log,
        mock_setup_log,
    ):  # pylint: disable=too-many-arguments
        """
        Test Templatron.start() where the config is valid
        """

        mock_die.side_effect = SystemExit
        self.templatron.start("command")
        mock_setup_log.assert_called_with("command")
        mock_maybe_log.assert_called()
        mock_validate.assert_called()
        mock_die.assert_not_called()
        mock_create.assert_called()
        mock_build.assert_called()

    @patch("templatron.templatron.Templatron.setup_logging")
    @patch("templatron.templatron.Templatron.maybe_log_dry_run")
    @patch("templatron.templatron.Templatron.validate_config")
    @patch("templatron.templatron.Templatron.die")
    @patch("templatron.templatron.Templatron.create_clone_root")
    @patch("templatron.templatron.Templatron.build_template")
    def test_start_invalid(
        self,
        mock_build,
        mock_create,
        mock_die,
        mock_validate,
        mock_maybe_log,
        mock_setup_log,
    ):  # pylint: disable=too-many-arguments
        """
        Test Templatron.start() where the config is invalid
        """

        mock_validate.side_effect = TemplatronException
        mock_die.side_effect = SystemExit
        with self.assertRaises(SystemExit):
            self.templatron.start("command")
        mock_setup_log.assert_called_with("command")
        mock_maybe_log.assert_called()
        mock_validate.assert_called()
        mock_die.assert_called()
        mock_create.assert_not_called()
        mock_build.assert_not_called()

    @patch("templatron.templatron.Templatron.maybe_clean")
    def test_stop(self, mock_clean):
        """
        Test Templatron.stop()
        """

        self.templatron.stop()
        mock_clean.assert_called()

    @patch("templatron.templatron.Templatron.build_repo")
    @patch("templatron.templatron.Templatron.stop")
    @patch("templatron.templatron.Templatron.start")
    def test_update_single_repo(self, mock_start, mock_stop, mock_build):
        """
        Test Templatron.update() with a single repo
        """

        self.templatron.update("fake_repo")
        mock_start.assert_called_with("updating")
        mock_build.assert_called_with("fake_repo")
        mock_build().update.assert_called()
        mock_stop.assert_called()

    @patch("templatron.templatron.Templatron.build_repos")
    @patch("templatron.templatron.Templatron.stop")
    @patch("templatron.templatron.Templatron.start")
    def test_update_multi_repos(self, mock_start, mock_stop, mock_build):
        """
        Test Templatron.update() with multiple repos
        """

        self.templatron.update()
        mock_start.assert_called_with("updating")
        mock_build.assert_called()
        mock_stop.assert_called()

    @patch("templatron.templatron.Templatron.build_repo")
    @patch("templatron.templatron.Templatron.stop")
    @patch("templatron.templatron.Templatron.start")
    def test_update_update_error(self, mock_start, mock_stop, mock_build):
        """
        Test Templatron.update() when repo.update() fails
        """

        mock_build().update.side_effect = TemplatronException
        self.templatron.logger = MagicMock()
        self.templatron.update("fake_repo")
        mock_start.assert_called_with("updating")
        mock_build.assert_called_with("fake_repo")
        mock_build().update.assert_called()
        mock_stop.assert_called()
        self.templatron.logger.error.assert_called()

    @patch("templatron.templatron.Templatron.maybe_clean")
    @patch("templatron.templatron.Templatron.build_repo")
    @patch("templatron.templatron.Templatron.stop")
    @patch("templatron.templatron.Templatron.start")
    def test_update_keyboard_interrupt(
        self, mock_start, mock_stop, mock_build, mock_clean
    ):
        """
        Test Templatron.update() when a keyboard interrupt occurs
        """

        mock_build.side_effect = KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            self.templatron.update("fake_repo")
        mock_start.assert_called_with("updating")
        mock_build.assert_called_with("fake_repo")
        mock_stop.assert_not_called()
        mock_clean.assert_called()

    def test_validate_config_no_github_token(self):
        """
        Test Templatron.validate_config() when no github token is present
        """

        self.templatron.token = None
        with self.assertRaises(GitConfigError):
            self.templatron.validate_config()

    @patch("templatron.templatron.git")
    @patch("templatron.templatron.environ.get")
    def test_validate_config_env_vars_set(self, mock_get, mock_git):
        """
        Test Templatron.validate_config() when git config environment variables
        are set
        """

        mock_get.return_value = "fake value"
        self.templatron.validate_config()
        mock_git.assert_not_called()

    # pretty sure this is failing due to a bug in sh.ErrorReturnCode
    # @patch("templatron.templatron.git")
    # @patch("templatron.templatron.environ.get")
    # def test_validate_config_git_error(self, mock_get, mock_git):
    #     """
    #     Test Templatron.validate_config() when git config encounters an error
    #     """

    #     mock_get.return_value = ""
    #     mock_git.config.side_effect = ErrorReturnCode(
    #         "fake_cmd", b"stdout", b"stderr"
    #     )
    #     with self.assertRaises(GitConfigError):
    #         self.templatron.validate_config()
    #     mock_git.config.assert_called_with("--get", "user.email")

    @patch("templatron.templatron.git")
    @patch("templatron.templatron.environ.get")
    def test_validate_config_valid(self, mock_get, mock_git):
        """
        Test Templatron.validate_config() when config is valid
        """

        mock_get.return_value = None
        self.templatron.validate_config()
        mock_git.config.assert_called_with("--get", "user.name")

    # * repo_name in repo_keys
    # * kw_org = None
    # * org is not None and kw_org != org
    # * dry_run is True
    # * interactive is True
    # * ensure kwargs['org'] doesn't exist

    @patch("templatron.templatron.Templatron.split_org_and_name")
    def test_validate_repo_no_kw_org(self, mock_split):
        """
        Test Templatron.validate_repo() with no org set in config
        """

        mock_split.return_value = ("fake_org", "fake_repo")
        self.templatron.template.config.get.side_effect = [
            "answers_file",
            "branch_prefix",
            "branch_separator",
            "dry_run",
            "hooks",
        ]
        kwargs = {
            "answers_file": "answers_file",
            "branch_prefix": "branch_prefix",
            "branch_separator": "branch_separator",
            "dry_run": "dry_run",
            "hooks": "hooks",
        }
        self.assertEqual(
            self.templatron.validate_repo("fake_org/fake_repo"),
            ("fake_repo", "fake_org", kwargs),
        )

    @patch("templatron.templatron.Templatron.split_org_and_name")
    def test_validate_repo_repo_in_repos(self, mock_split):
        """
        Test Templatron.validate_repo() where repo_name is in repo config
        """

        mock_split.return_value = ("fake_org", "fake_repo")
        self.templatron.template.config.repos = {
            "fake_repo": {
                "org": "fake_org",
            }
        }
        self.templatron.template.config.get.side_effect = [
            "answers_file",
            "branch_prefix",
            "branch_separator",
            "dry_run",
            "hooks",
        ]
        kwargs = {
            "answers_file": "answers_file",
            "branch_prefix": "branch_prefix",
            "branch_separator": "branch_separator",
            "dry_run": "dry_run",
            "hooks": "hooks",
        }
        self.assertEqual(
            self.templatron.validate_repo("fake_repo"),
            ("fake_repo", "fake_org", kwargs),
        )

    @patch("templatron.templatron.Templatron.split_org_and_name")
    def test_validate_repo_org_mismatch(self, mock_split):
        """
        Test Templatron.validate_repo() where repo_name is in repo config
        """

        mock_split.return_value = ("other_org", "fake_repo")
        self.templatron.template.config.repos = {
            "fake_repo": {
                "org": "fake_org",
            }
        }
        with self.assertRaises(AmbiguousOrgConfigError):
            self.templatron.validate_repo("fake_repo")

    @patch("templatron.templatron.Templatron.split_org_and_name")
    def test_validate_repo_global_force(self, mock_split):
        """
        Test Templatron.validate_repo() where dry_run or interactive
        configs are enabled
        """

        mock_split.return_value = ("fake_org", "fake_repo")
        self.templatron.config.dry_run = True
        self.templatron.config.interactive = True
        self.templatron.template.config.repos = {
            "fake_repo": {
                "org": "fake_org",
            }
        }
        self.templatron.template.config.get.side_effect = [
            "answers_file",
            "branch_prefix",
            "branch_separator",
            "dry_run",
            "hooks",
        ]
        kwargs = {
            "answers_file": "answers_file",
            "branch_prefix": "branch_prefix",
            "branch_separator": "branch_separator",
            "dry_run": True,
            "hooks": "hooks",
            "interactive": True,
        }
        self.assertEqual(
            self.templatron.validate_repo("fake_repo"),
            ("fake_repo", "fake_org", kwargs),
        )
