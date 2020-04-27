from unittest import TestCase
import wiki.web.user as user
import os.path as path


class Test(TestCase):
    def test_user_create(self):
        userFilePath = "C:\\git_repositories\\wikielodeon\\user\\"
        getUser = user.UserManager(userFilePath)
        new_user = getUser.get_user('root')
        self.assertTrue(new_user.get('password') == 'admin')

    def test_if_new_user_added_is_active_active(self):
        userFilePath = "C:\\git_repositories\\wikielodeon\\user\\"
        getUser = user.UserManager(userFilePath)
        new_usr = getUser.get_user("root")
        self.assertTrue(new_usr.is_active())

    def test_if_new_user_added_is_not_autheticated_offine(self):
        userFilePath = "C:\\git_repositories\\wikielodeon\\user\\"
        getUser = user.UserManager(userFilePath)
        new_usr = getUser.get_user("adel")
        self.assertTrue(not new_usr.is_authenticated())