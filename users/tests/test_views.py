from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from orders.models import ShoppingCart
from users.models import CustomUser, Group, UserAddress
from users.permissions import is_in_group
from users.serializers import GroupPermissionsSerializer


class TestUsers(TestCase):
    # for logging in test user to get cookeis to test auth
    def login_test_user(self):
        url = "/users/login/"
        data = {
            "username": "testi1@turku.fi",
            "password": "turku",
        }
        response = self.client.post(url, data, content_type="application/json")
        user = CustomUser.objects.get(username="testi1@turku.fi")
        return user

    def login_test_admin(self):
        url = "/users/login/"
        data = {
            "username": "admin",
            "password": "admin",
        }
        response = self.client.post(url, data, content_type="application/json")
        user = CustomUser.objects.get(username="admin")
        return user

    def setUp(self):
        groups = ["user_group", "admin_group", "storage_group", "bicycle_group"]
        for group in groups:
            group_object = Group(name=group)
            group_object.save()

        super = CustomUser.objects.create_superuser(username="super", password="super")
        for group in Group.objects.all():
            group.user_set.add(super)

        user_set = CustomUser.objects.create_user(
            first_name="first_name",
            last_name="last_name",
            email="testi1@turku.fi",
            phone_number="phone_number",
            password="turku",
            address="address",
            zip_code="zip_code",
            city="city",
            username="testi1@turku.fi",
            joint_user="false",
        )

        user2_set = CustomUser.objects.create_user(
            first_name="first_name",
            last_name="last_name",
            email="testi2@turku.fi",
            phone_number="phone_number",
            password="turku",
            address="address",
            zip_code="zip_code",
            city="city",
            username="testimies",
            joint_user="true",
        )

        user3_set = CustomUser.objects.create_user(
            first_name="admin",
            last_name="adming",
            email="admin@turku.fi",
            phone_number="admin",
            password="admin",
            address="admin",
            zip_code="admin",
            city="admin",
            username="admin",
            joint_user="true",
        )
        for group in Group.objects.all():
            group.user_set.add(user3_set)

    def test_setup(self):
        print("EKA, count user objs after setup?: ", CustomUser.objects.count())
        # self.assertNotEqual(2, 3)
        self.assertEqual(
            CustomUser.objects.count(),
            4,
            "testing setup, somethigng went wrong with setup",
        )

    def test_get_users_forbidden(self):
        """
        Testing 404 responses from urls, so they exist
        """
        print("TOKA")
        url_list = [
            "/users/create/",
            "/users/login/",
            "/users/login/refresh/",
            "/users/logout/",
            "/users/",
        ]

        for url in url_list:
            response = self.client.get(url)
            self.assertNotEqual(
                response.status_code, 404, f"{url} seemingly cant be reached"
            )

    def test_post_user_creation(self):
        print("KOLMAS")
        current_user_number = CustomUser.objects.count()
        url = "/users/create/"

        # test GET not alloweed
        response = self.client.get(url)
        self.assertEqual(
            response.status_code, 405, "testing GET response, shoul not be allowed"
        )

        # test response with imperfect data
        imperfect_data = {
            "last_name": "tstilä",
            "email": "testingly@sssss.fi",
        }
        response = self.client.post(
            url, imperfect_data, content_type="application/json"
        )
        self.assertEqual(
            response.status_code, 400, "user creation should fail with not enough data"
        )

        # test response with correct data for normal user creation
        data = {
            "first_name": "testi",
            "last_name": "tstilä",
            "email": "testingly@turku.fi",
            "phone_number": "54519145",
            "password": "1234",
            "address": "testiläntie 12",
            "zip_code": "12552",
            "city": "TESTIKAUPUNKI",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code, 201, "user creation was not succesfull with POST"
        )
        # print("luonnin jälkee: ", CustomUser.objects.count())
        after_creation = CustomUser.objects.count()
        self.assertNotEqual(
            current_user_number,
            after_creation,
            "user number should be higher after user is created somethign failing",
        )
        current_user_number = CustomUser.objects.count()

        try:
            user = CustomUser.objects.get(username="testingly@turku.fi")
            # print("not derp")
        except ObjectDoesNotExist:
            # print("derp")
            user = None

        self.assertIsNotNone(user, "user was not created with correct data")
        # print("username: ", user.username)
        self.assertEqual(
            user.email, user.username, "normal user should have same username and email"
        )

        # testing that same user creation
        response = self.client.post(url, data, content_type="application/json")
        self.assertNotEqual(
            response.status_code,
            201,
            "user creation should not go through with same user info",
        )

        # testing that shopping cart was created for created user
        self.assertNotEqual(
            ShoppingCart.objects.filter(user=user).count(),
            0,
            "sometghing wrong with shopping cart creation for user",
        )

        self.assertTrue(
            is_in_group(user, "user_group"),
            "user isnt part of user group after creation",
        )

        # test taht not allowed webdomain doesnt go thru
        data["email"] = "thisiswrongemaildomain@wrong_email_domain.fi"
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code, 400, "should get bad request with wrong email domain"
        )

        # test taht not allowed webdomain doesnt go thru
        data["email"] = "thisiswrongemaildomain"
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code, 400, "should get bad request with wrong email(no @)"
        )

        # test response with correct data for joint user creation wrongly and then correct
        data = {
            "first_name": "testi",
            "last_name": "tstilä",
            "email": "testingly@turku.fi",
            "phone_number": "54519145",
            "password": "1234",
            "joint_user": "true",
            "username": "",
            "address": "testiläntie 12",
            "zip_code": "12552",
            "city": "TESTIKAUPUNKI",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            400,
            "Joint user creation not working, username check fails, empty should not go through",
        )

        data = {
            "first_name": "testi",
            "last_name": "tstilä",
            "email": "testingly@turku.fi",
            "phone_number": "54519145",
            "password": "1234",
            "joint_user": "true",
            "username": "testin päiväkoti",
            "address": "testiläntie 12",
            "zip_code": "12552",
            "city": "TESTIKAUPUNKI",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            201,
            "Joint user creation not working with correct data",
        )

        after_creation = CustomUser.objects.count()
        self.assertNotEqual(
            current_user_number,
            after_creation,
            "user number should be higher after user is created somethign failing",
        )
        current_user_number = CustomUser.objects.count()

        try:
            user = CustomUser.objects.get(username="testin päiväkoti")
            # print("not derp")
        except ObjectDoesNotExist:
            # print("derp")
            user = None

        self.assertIsNotNone(user, "user was not created with correct data")

        self.assertNotEqual(
            user.email,
            user.username,
            "joint user should have not same username and email",
        )

    def test_order(self):
        print("NELAJS, count user objs after setup?: ", CustomUser.objects.count())
        self.assertEqual(CustomUser.objects.count(), CustomUser.objects.count())

    def test_user_login(self):
        # testing user login
        print("VIIIDES")
        # wrong
        url = "/users/login/"
        data = {
            "username": "kek",
            "password": "kuk",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            204,
            "wrong status code when wrong login info",
        )
        # right
        data = {
            "username": "testi1@turku.fi",
            "password": "turku",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            200,
            "wrong status codew coming when data loging data is right",
        )

        # check that cookies were created in login
        self.assertIn(
            "access_token",
            self.client.cookies.keys(),
            "no access token in cookies after login",
        )
        self.assertIn(
            "refresh_token",
            self.client.cookies.keys(),
            "no refresh token in cookies after login",
        )

    def test_user_refresh(self):
        print("KUUDES")
        # print("cookies: ", self.client.cookies.keys())

        # testing the return value without cookies
        url = "/users/login/refresh/"
        data = {}
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            204,
            "wrong status code coming when no cookies",
        )

        # testing that access token refreshes goes thorugh
        self.login_test_user()
        # print("cookies: ", self.client.cookies.keys())
        access_token_before = self.client.cookies["access_token"].value
        # print("access: ", access_token_before)

        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            200,
            "wrong status code coming when cookies are send",
        )

        access_token_after = self.client.cookies["access_token"].value

        # testing taht access token was refreshes
        self.assertNotEqual(
            access_token_before,
            access_token_after,
            "accesss token same afer refresh",
        )

        # testing invalid refresh token
        self.client.cookies.__setitem__("refresh_token", "ffffffffff")
        # print("refresh token : ", self.client.cookies["refresh_token"].value)
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            401,
            "wrong status code coming when invalid refresh token",
        )

    def test_user_logout(self):
        print("SEITSEMÄAS")
        url = "/users/logout/"
        data = {}
        # grabbing the jwt tokens (logging in)
        self.login_test_user()
        # print("cookies: ", self.client.cookies.keys())
        refresh_token_before = self.client.cookies["refresh_token"].value
        access_token_before = self.client.cookies["access_token"].value
        # print("refresh token : ", self.client.cookies["refresh_token"].value)
        # print("access token : ", self.client.cookies["access_token"].value)

        # logging out and hten checking tokens are empty/gone
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code, 200, "not getting right http status code on success"
        )
        # print("cookies: ", self.client.cookies.keys())
        # print("refresh token : ", self.client.cookies["refresh_token"].value)
        # print("access token : ", self.client.cookies["access_token"].value)
        refresh_token_after = self.client.cookies["refresh_token"].value
        access_token_after = self.client.cookies["access_token"].value

        self.assertNotEqual(
            access_token_before,
            access_token_after,
            "accesss token same after logout, should be gone/empty",
        )
        self.assertNotEqual(
            refresh_token_before,
            refresh_token_after,
            "refresh token same afer logout, should be gone/empty",
        )

    def test_user_detail(self):
        # testing getting user information and allowed groups working for view
        print("KAHDEKSASS")
        url = "/users/"
        # anonymous
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(
            response.status_code, 403, "wihtout logging in should be forbidden"
        )
        response = self.client.post(url, content_type="application/json")
        self.assertEqual(
            response.status_code, 403, "wihtout logging in should be forbidden"
        )
        url = "/users/1/"
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(
            response.status_code, 403, "wihtout logging in should be forbidden"
        )
        url = "/users/52165445764567467668745983495834956349856394568934659834659834698596516/"
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(
            response.status_code, 403, "wihtout logging in should be forbidden"
        )

        url = "/users/"
        # normal user
        self.login_test_user()
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(
            response.status_code, 403, "normal user should not  be allowed"
        )
        url = "/users/1/"
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(
            response.status_code, 403, "wihtout logging in should be forbidden"
        )
        url = "/users/52165445764567467668745983495834956349856394568934659834659834698596516/"
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(
            response.status_code, 403, "wihtout logging in should be forbidden"
        )

        url = "/users/"
        # admin suer
        self.login_test_admin()
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(response.status_code, 200, "admin user should go thorugh")
        response = self.client.post(url, content_type="application/json")
        self.assertEqual(response.status_code, 405, "POST should not exist/alllowed")

        # print("test user id: ", CustomUser.objects.get(username="testi1@turku.fi").id)
        test_user_id = CustomUser.objects.get(username="testi1@turku.fi").id
        url = f"/users/{test_user_id}/"
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(response.status_code, 200, "admin user should go thorugh")
        url = "/users/52165445764567467668745983495834956349856394568934659834659834698596516/"
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(
            response.status_code,
            204,
            "admin user should go thorugh with 204 on non existant user",
        )

    def test_user_detail_loggedin(self):
        print("YSIIIIiiii")
        url = "/user/"
        # anonymous
        response = self.client.get(url, content_type="application/json")
        # print(response.status_code)
        self.assertEqual(
            response.status_code, 403, "wihtout logging in should be forbidden"
        )

        # normal user
        user = self.login_test_user()
        # print(self.client.cookies.keys(), self.client.cookies["access_token"])
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(
            response.status_code, 200, "when user is logged should go thorugh"
        )
        response_json = response.json()
        print("vastauksen id: ", response_json["id"], "  , id databasesta: ", user.id)
        self.assertEqual(
            response_json["id"],
            user.id,
            "user id in resposne should be same as logged in user",
        )

    def test_group_names(self):
        # testing that you can get the groups
        print("KYMMMPPPIIIII")
        url = "/users/groups/"
        self.login_test_user()
        response = self.client.get(url, content_type="application/json")
        response_JSON = response.json()
        # print(response_JSON)
        self.assertTrue(
            any("user_group" in dict.values() for dict in response_JSON),
            "user_group ei löydy",
        )
        self.assertTrue(
            any("admin_group" in dict.values() for dict in response_JSON),
            "admin_group ei löydy",
        )
        self.assertTrue(
            any("storage_group" in dict.values() for dict in response_JSON),
            "storage_group ei löydy",
        )
        self.assertTrue(
            any("bicycle_group" in dict.values() for dict in response_JSON),
            "bicycle_group ei löydy",
        )

    def test_group_permission(self):
        # test taht permission change is working
        # print("YKSITOISTAAAaaaa")
        user_for_testing = CustomUser.objects.get(username="testi1@turku.fi")
        first = GroupPermissionsSerializer(user_for_testing)
        groups_before = first.data["groups"]
        # print(
        #     "aluksi griuo ID mihin kuuluu: ", first.data["groups"]
        # )  # <<<-----------------------
        url = f"/users/groups/permission/{user_for_testing.id}/"
        self.login_test_user()
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(
            response.status_code, 403, "should be forbidden for normal user"
        )
        response = self.client.put(url, content_type="application/json")
        self.assertEqual(
            response.status_code, 403, "should be forbidden for normal user"
        )
        self.login_test_admin()
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(response.status_code, 200, "admin should pass through")
        admin_group_id = Group.objects.get(name="admin_group")
        user_group_id = Group.objects.get(name="user_group")
        first_response_json = response.json()
        # print(first_response_json,  first_response_json["groups"])
        data = {
            "groups": [
                admin_group_id.id,
                user_group_id.id,
            ]
        }
        response = self.client.patch(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            200,
            "admin should able to change succesfully permissions",
        )
        second_response_json = response.json()
        # print(second_response_json["groups"])
        self.assertNotEqual(
            first_response_json["groups"],
            second_response_json["groups"],
            "admin should able to change permissions",
        )

        user2 = CustomUser.objects.get(username="testi1@turku.fi")
        second = GroupPermissionsSerializer(user2)
        groups_after = second.data["groups"]
        # print("toinen muutoksen jälkee mihin kuuluu: ", second.data["groups"])
        # print("eka: ", first.data["groups"], "toka: ", second.data["groups"])
        # self.assertNotEqual(
        #     first.data["groups"],
        #     second.data["groups"],
        #     "group permissions in database shoudl change",
        # )
        # print("groups are before and after: ", groups_before, "     ", groups_after)
        self.assertNotEqual(
            groups_before,
            groups_after,
            "group permissions in database shoudl change",
        )

    def test_updating_user_info_with_user(self):
        # test updating own user info as user
        print("KAKSTOISTAA!!!!")
        url = "/users/update/"

        response = self.client.put(
            url,
        )
        self.assertEqual(
            response.status_code, 401, "should not have access if not user"
        )
        user = self.login_test_user()
        print("user: ", user, "name: ", user.name, " phone : ", user.phone_number)
        data = {"name": "Kinkku Kinkku!222", "phone_number": "kinkku!2222"}
        print(data)
        response = self.client.put(url, data, content_type="application/json")
        user2 = CustomUser.objects.get(id=user.id)
        print("user: ", user, "name: ", user.name, " phone : ", user.phone_number)
        print("user: ", user2, "name: ", user2.name, " phone : ", user2.phone_number)

    # def test_updating_user_info_with_admin(self):
    #     #test updating other user info as admin
    #     pass
