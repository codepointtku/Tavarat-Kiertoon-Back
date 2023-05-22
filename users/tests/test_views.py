from django.conf import settings
from django.contrib.auth.models import Group
from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, override_settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from orders.models import ShoppingCart
from users.models import CustomUser, UserAddress
from users.permissions import is_in_group
from users.serializers import GroupPermissionsSerializer


# check the changed data is the same data as the changed data instead htat jsut the data has changed.
class TestUsers(TestCase):
    # function for logging in test user to get cookeis to test normal user
    def login_test_user(self):
        url = "/users/login/"
        data = {
            "username": "testi1@turku.fi",
            "password": "turku",
        }
        response = self.client.post(url, data, content_type="application/json")
        user = CustomUser.objects.get(username="testi1@turku.fi")
        return user

    # function for logging in test admin user to get cookeis to test admin user
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
        )
        user_set.is_active = True
        user_set.save()

        user2_set = CustomUser.objects.create_user(
            first_name="first_name",
            last_name="last_name",
            email="testi2@turku.fi",
            phone_number="phone_number",
            password="turku",
            address="testi",
            zip_code="testi",
            city="tessti",
            username="testimies",
        )
        user2_set.is_active = True
        user2_set.save()

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
        )
        user3_set.is_active = True
        user3_set.save()
        for group in Group.objects.all():
            group.user_set.add(user3_set)

    def test_get_users_forbidden(self):
        """
        Testing 404 responses from urls, so they exist
        """
        # getting objects which id's get used in urls
        user_for_testing = CustomUser.objects.get(username="testi1@turku.fi")
        address_for_testing = UserAddress.objects.get(address="admin")

        # list of urls that need to be checked that they exist
        url_list = [
            "/users/create/",
            "/users/login/",
            "/users/login/refresh/",
            "/users/logout/",
            "/users/",
            f"/users/{user_for_testing.id}/",
            "/user/",
            "/users/groups/",
            f"/users/{user_for_testing.id}/groups/permission/",
            f"/users/{user_for_testing.id}/",
            "/user/address/edit/",
            f"/user/address/edit/{address_for_testing.id}/",
            f"/users/address/{address_for_testing.id}/",
            "/users/password/resetemail/",
            "/users/password/reset/",
            "/users/password/reset/1/1/",
            "/users/activate/",
        ]

        # goign thorugh the urls
        for url in url_list:
            response = self.client.get(url)
            self.assertNotEqual(
                response.status_code, 404, f"{url} seemingly cant be reached"
            )

    def test_post_user_creation(self):
        """
        Test for testing user creation
        """
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

        # checking from database taht the user was created by comapring user count
        after_creation = CustomUser.objects.count()
        self.assertNotEqual(
            current_user_number,
            after_creation,
            "user number should be higher after user is created somethign failing",
        )
        current_user_number = CustomUser.objects.count()

        # testing that the users info is rihgt after creation
        try:
            user = CustomUser.objects.get(username="testingly@turku.fi")
        except ObjectDoesNotExist:
            user = None

        self.assertIsNotNone(user, "user was not created with correct data")
        self.assertEqual(
            user.email, user.username, "normal user should have same username and email"
        )

        # testing user creation with already existing user info
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

        # testing that user was correctly added to user_group
        self.assertTrue(
            is_in_group(user, "user_group"),
            "user isnt part of user group after creation",
        )

        # test that not allowed webdomain doesn't go through
        data["email"] = "thisiswrongemaildomain@wrong_email_domain.fi"
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code, 400, "should get bad request with wrong email domain"
        )

        # non email adress test
        data["email"] = "thisiswrongemaildomain"
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code, 400, "should get bad request with wrong email(no @)"
        )

        # test response with correct data for joint user creation wrongly and then correct
        # wrong data (invalid username)
        data = {
            "first_name": "testi",
            "last_name": "tstilä",
            "email": "testingly@turku.fi",
            "phone_number": "54519145",
            "password": "1234",
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

        # with right data (username)
        data["username"] = "testin päiväkoti"

        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            201,
            "Joint user creation not working with correct data",
        )

        # checking that user was created in database sucesfully
        after_creation = CustomUser.objects.count()
        self.assertNotEqual(
            current_user_number,
            after_creation,
            "user number should be higher after user is created somethign failing",
        )
        current_user_number = CustomUser.objects.count()

        try:
            user = CustomUser.objects.get(username="testin päiväkoti")
        except ObjectDoesNotExist:
            user = None

        self.assertIsNotNone(user, "user was not created with correct data")

        # checking that joint user user name and email is correctly set, as in has user name instead of email
        self.assertNotEqual(
            user.email,
            user.username,
            "joint user should have not same username and email",
        )

    def test_user_login(self):
        """
        Test to test login functionality
        """
        # wrong login info
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
        # correct login info
        data = {
            "username": "testi1@turku.fi",
            "password": "turku",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            200,
            "wrong status code coming when data loging data is right",
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

        # checking that users groups they should belong to are in return json
        self.assertTrue(
            ("user_group" in response.json()["groups"]),
            "did not find user group in login response",
        )

    def test_user_refresh(self):
        """
        test to test token refreshing functionality
        """

        # testing the return value without cookies
        url = "/users/login/refresh/"
        data = {}
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            204,
            "wrong status code coming when no cookies",
        )

        # testing that access token refreshes goes through
        self.login_test_user()
        access_token_before = self.client.cookies["access_token"].value

        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            200,
            "wrong status code coming when cookies are send",
        )

        # checking that users groups they should belong to are in return json
        self.assertTrue(
            ("user_group" in response.json()["groups"]),
            "did not find user group in refresh response",
        )

        access_token_after = self.client.cookies["access_token"].value

        # testing that access token was refreshed
        self.assertNotEqual(
            access_token_before,
            access_token_after,
            "accesss token same after refresh",
        )

        # testing invalid refresh token
        self.client.cookies.__setitem__("refresh_token", "ffffffffff")
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            401,
            "wrong status code coming when invalid refresh token",
        )

    def test_user_logout(self):
        """
        test for testing logout functionality
        """
        url = "/users/logout/"
        data = {}
        self.login_test_user()
        refresh_token_before = self.client.cookies["refresh_token"].value
        access_token_before = self.client.cookies["access_token"].value

        # logging out and then checking tokens are empty/gone
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code, 200, "not getting right http status code on success"
        )

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
            "refresh token same after logout, should be gone/empty",
        )

    def test_user_detail(self):
        """
        test for testing user information views
        """

        # testing getting user information and allowed groups working for view
        url = "/users/"
        # anonymous user responses
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(
            response.status_code, 403, "without logging in should be forbidden"
        )
        response = self.client.post(url, content_type="application/json")
        self.assertEqual(
            response.status_code, 403, "without logging in should be forbidden"
        )
        url = "/users/1/"
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(
            response.status_code, 401, "without logging in should be unauthorized"
        )
        url = "/users/99999952165445764567467668745983495834956349856394568934659834659834698596516/"
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(
            response.status_code, 401, "without logging in should be unauthorized"
        )

        url = "/users/"
        # normal user responses
        self.login_test_user()
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(response.status_code, 403, "normal user should not be allowed")
        url = "/users/1/"
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(response.status_code, 403, "normal user should not be allowed")
        url = "/users/52165445764567467668745983495834956349856394568934659834659834698596516/"
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(response.status_code, 403, "normal user should not be allowed")

        url = "/users/"
        # admin user responses
        self.login_test_admin()
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(response.status_code, 200, "admin user should go thorugh")
        response = self.client.post(url, content_type="application/json")
        self.assertEqual(response.status_code, 405, "POST should not exist/alllowed")

        # getting user id that actually exists for test
        test_user_id = CustomUser.objects.get(username="testi1@turku.fi").id
        url = f"/users/{test_user_id}/"
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(response.status_code, 200, "admin user should go thorugh")
        # non existing user
        url = "/users/52165445764567467668745983495834956349856394568934659834659834698596516/"
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(
            response.status_code,
            204,
            "admin user should go thorugh with 204 on non existant user",
        )

    def test_user_detail_loggedin(self):
        """
        Test for testing getitng logged in users stuff
        """
        url = "/user/"
        # anonymous
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(
            response.status_code, 401, "wihtout logging in should be unauthorized"
        )

        # normal user
        user = self.login_test_user()
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(
            response.status_code, 200, "when user is logged should go thorugh"
        )

        # check that it is users own info thats gotten
        response_json = response.json()
        self.assertEqual(
            response_json["id"],
            user.id,
            "user id in resposne should be same as logged in user",
        )

    def test_group_names(self):
        """
        test for checking the group names exist in database and you can get them
        """
        url = "/users/groups/"
        self.login_test_user()
        response = self.client.get(url, content_type="application/json")
        response_JSON = response.json()
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
        """
        Test for checking that permission changes go through
        """
        # actually existin user id get for testing
        user_for_testing = CustomUser.objects.get(username="testi1@turku.fi")
        first = GroupPermissionsSerializer(user_for_testing)
        groups_before = first.data["groups"]
        url = f"/users/{user_for_testing.id}/groups/permission/"

        # testing that normal non admin user cant do the change
        self.login_test_user()
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(
            response.status_code, 403, "should be forbidden for normal user"
        )
        response = self.client.put(url, content_type="application/json")
        self.assertEqual(
            response.status_code, 403, "should be forbidden for normal user"
        )

        # testing that admin can change permissions
        self.login_test_admin()
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(response.status_code, 200, "admin should pass through")

        # getting the correct groups and their id so they can be changed
        admin_group = Group.objects.get(name="admin_group")
        user_group = Group.objects.get(name="user_group")
        first_response_json = response.json()
        data = {
            "groups": [
                admin_group.id,
                user_group.id,
            ]
        }
        response = self.client.patch(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            200,
            "admin should able to succesfully change permissions",
        )
        second_response_json = response.json()
        # checking that the permissions are actually changed in json
        self.assertNotEqual(
            first_response_json["groups"],
            second_response_json["groups"],
            "admin should able to change permissions",
        )

        # checking that the change actually exist in database
        user2 = CustomUser.objects.get(username="testi1@turku.fi")
        second = GroupPermissionsSerializer(user2)
        groups_after = second.data["groups"]
        self.assertNotEqual(
            groups_before,
            groups_after,
            "group permissions in database should change",
        )

    def test_updating_user_info_with_user(self):
        """
        test for users changing their own info
        """
        url = "/user/"

        # test without logging in (forbidden response)
        response = self.client.put(url)
        self.assertEqual(
            response.status_code, 401, "should not have access if not user"
        )

        # testing getting own info
        user = self.login_test_user()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, "should have access user")

        # testing changing the info if succesfull in database
        data = {"name": "Kinkku Kinkku!222", "phone_number": "kinkku!2222"}
        response = self.client.put(url, data, content_type="application/json")
        user2 = CustomUser.objects.get(id=user.id)

        # check the changed data is the same data as the changed data instead that just the data has changed.
        self.assertNotEqual(user.name, user2.name, "user name should have changed")
        self.assertNotEqual(
            user.phone_number,
            user2.phone_number,
            "user phone number should have changed",
        )

    def test_updating_user_info_with_admin(self):
        """
        test for testing admin changin other users info
        """

        # get existing users id for testing
        user_for_testing = CustomUser.objects.get(username="testi1@turku.fi")
        url = f"/users/{user_for_testing.id}/"

        # test response when not logged in
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            401,
            "should not have access if not user or admin user",
        )
        # as normal user
        user = self.login_test_user()
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            403,
            "should not have access as normal user",
        )

        # as admin user
        user = self.login_test_admin()
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            200,
            "admin user should pass through",
        )

        # changing the user info
        user1 = CustomUser.objects.get(username="testi1@turku.fi")
        user1_info = [user1.name, user1.phone_number]
        data = {"name": "Kinkku Kinkku!222", "phone_number": "2222222"}
        response = self.client.put(url, data, content_type="application/json")

        # cheking that the info has changed in database
        user2 = CustomUser.objects.get(username="testi1@turku.fi")
        user2_info = [user2.name, user2.phone_number]
        self.assertNotEqual(user1_info, user2_info, "users info should have cahnged")
        self.assertEqual(user2.name, "Kinkku Kinkku!222", "user info changeed wrongly")
        self.assertEqual(user2.phone_number, "2222222", "user info changeed wrongly")

    def test_user_address(self):
        """
        test for testing user changing his own addressess
        """
        url = "/user/address/edit/"

        # test response as anon
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            401,
            "should not have access if not user",
        )

        # test response when logged in
        user = self.login_test_user()
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            200,
            "should have access if user",
        )

        # remember the address count at start
        address_count = UserAddress.objects.filter(user=user).count()

        address1 = UserAddress.objects.filter(user=user).first()
        data = {
            "zip_code": "6666666666",
            "id": address1.id,
        }
        zip_before_update = address1.zip_code
        # checking response is right
        response = self.client.put(url, data=data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            200,
            "put/update should go through as user",
        )

        # checking that values have changed in database
        address1 = UserAddress.objects.filter(user=user).first()
        zip_after_update = address1.zip_code
        self.assertNotEqual(
            zip_before_update,
            zip_after_update,
            "if update goes through zip code should have changed",
        )

        # testing that if user and owner of address dont match things shouldnt go thorugh
        self.login_test_admin()
        response = self.client.put(url, data=data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            204,
            "put/update should not go through as different user",
        )
        self.login_test_user()

        # testing that things should not go thorugh without address id to update
        data = {
            "zip_code": "77777777",
        }
        response = self.client.put(url, data=data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            204,
            "put/update should not go through without address id for update",
        )

        # testing new address additions
        data = {
            "address": "testikatula 1818",
            "zip_code": "10101",
            "city": "testi_1",
            "user": user.id,
        }

        response = self.client.post(url, data=data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            200,
            "should go through as user",
        )
        address_count_2 = UserAddress.objects.filter(user=user).count()

        # testing that the new address is in database
        self.assertNotEqual(
            address_count,
            address_count_2,
            "shold have different number of addresses after adding address for same user",
        )

        data = {
            "id": address1.id,
        }

        url = f"/user/address/edit/{address1.id}/"
        # testing that non owner of address delete should not go through
        self.login_test_admin()
        response = self.client.delete(url, data=data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            204,
            "should not go through as user and address owner is different",
        )

        # testing that user can delete his own address
        self.login_test_user()
        response = self.client.delete(url, data=data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            200,
            "should go through as user and adress owner is same in delete",
        )
        # checking that database was updated
        address_count_3 = UserAddress.objects.filter(user=user).count()
        self.assertNotEqual(
            address_count_2, address_count_3, "after deletion count should be different"
        )

    def test_user_address_as_admin(self):
        """
        Test for testing admins rights to change adressess
        """
        # gettign address to test
        address_for_testing = UserAddress.objects.get(address="testi")
        address_id = address_for_testing.id
        url = f"/users/address/{address_id}/"

        # testing response for anons
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            401,
            "should not have access if not user",
        )

        # testing response as non admin
        self.login_test_user()
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            403,
            "should not have access if not admin",
        )

        # testing response as admin
        self.login_test_admin()
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            200,
            "should have access if admin",
        )

        # saving data at first for comparison later
        data_before = {
            "address": address_for_testing.address,
            "zip_code": address_for_testing.zip_code,
            "city": address_for_testing.city,
        }

        # testing changing data
        data = {
            "address": "muutos",
            "zip_code": "muutos",
            "city": "muutos",
        }
        response = self.client.patch(url, data=data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            200,
            "update patch should go thourgh",
        )
        address_for_testing = UserAddress.objects.get(id=address_id)
        data_after = {
            "address": address_for_testing.address,
            "zip_code": address_for_testing.zip_code,
            "city": address_for_testing.city,
        }

        # checking data has changed in database after update
        self.assertEqual(data_before, data_before)
        self.assertNotEqual(
            data_before, data_after, "the data should have been updated in database"
        )

        # testing that deleting user address works
        response = self.client.delete(url, content_type="application/json")
        with self.assertRaises(ObjectDoesNotExist, msg="adress was not deleted"):
            UserAddress.objects.get(id=address_id)

    def test_password_reset(self):
        """
        Test for testing password reset functionality
        """
        # urls required for tests
        url = "/users/password/resetemail/"
        url2 = "/users/password/reset/"
        url3 = settings.PASSWORD_RESET_URL_FRONT

        data = {"username": "tottally not should exist user name"}
        # testing invalid user, still should get 200 for security reasons but mail shoudnt be sent as user doesnt exist
        response = self.client.post(url, data=data, content_type="application/json")
        self.assertEqual(
            response.status_code, 200, "should get 200 even on non existing username"
        )
        self.assertEqual(
            len(mail.outbox),
            0,
            "mail should not have been sent when incorrect username",
        )

        data = {"username": "testimies"}
        response = self.client.post(url, data=data, content_type="application/json")
        self.assertEqual(
            response.status_code, 200, "should go thorugh with existing username"
        )

        # setting user as in_active to test that it turns to active staus
        user = CustomUser.objects.get(username="testimies")
        user.is_acivete = False
        user.save()

        # checking the front url is in reset email
        self.assertTrue(
            (settings.PASSWORD_RESET_URL_FRONT in mail.outbox[0].body),
            "password reset front url should be in reset email",
        )

        # grabbing the link from the email that was sent, and putting it into form that can be used with test
        end_part_of_email_link = mail.outbox[0].body.split(url3)
        the_parameters = end_part_of_email_link[1].split("/")
        # par 0 should be encoded uid, par 1 the token for reset

        # test that can get ok reponse from the reset url
        response = self.client.get(url2)
        self.assertEqual(
            response.status_code, 200, "should go thorugh without thigns happening"
        )

        # testing reponse with various non valid parameters
        data = {
            "new_password": "a",
            "new_password_again": "b",
            "uid": "a",
            "token": "a",
        }
        # non matching pws
        response = self.client.post(url2, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            204,
            "should get wrongly stuff with wrong pw",
        )

        data = {
            "new_password": "a",
            "new_password_again": "a",
            "uid": "a",
            "token": "a",
        }

        # wrong kind of encoded uid
        response = self.client.post(url2, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            204,
            "should get wrongly stuff with wrong uid",
        )

        # testataan ei oikealla uidllä jota ei olemassa
        uid = urlsafe_base64_encode(force_bytes(-1))
        data = {
            "new_password": "a",
            "new_password_again": "a",
            "uid": uid,
            "token": "a",
        }
        response = self.client.post(url2, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            204,
            "should get wrongly stuff with non existant uid",
        )

        data = {
            "new_password": "a",
            "new_password_again": "a",
            "uid": the_parameters[0],
            "token": "a",
        }
        # testing response with non  valid token
        response = self.client.post(url2, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            204,
            "should get wrongly stuff with wrong token",
        )

        # lisää tarkistus että token ja uid on oikein mutta salasana ei täsmää
        data = {
            "new_password": "a",
            "new_password_again": "c",
            "uid": the_parameters[0],
            "token": the_parameters[1],
        }
        response = self.client.post(url2, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            204,
            "should get wrongly stuff with wrong pw but uid and token right",
        )

        data = {
            "new_password": "a",
            "new_password_again": "a",
            "uid": the_parameters[0],
            "token": the_parameters[1],
        }
        # testing response with correct paramateres (should go though)
        response = self.client.post(url2, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            200,
            "should go thorugh with correct parameters",
        )

        # testing that token get properly used and cant be used anymore
        response = self.client.post(url2, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            204,
            "should not go thorugh as token should be used",
        )

        # testing that user active status was turned on
        user = CustomUser.objects.get(username="testimies")
        self.assertTrue(user.is_active, "user should be active after password reset")

        # testing login with old pw
        url = "/users/login/"
        data = {
            "username": "testimies",
            "password": "turku",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            204,
            "should not be able to login with old pw",
        )

        # testing login with new pw
        data = {
            "username": "testimies",
            "password": "a",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            200,
            "should be able to login with new pw",
        )

    def test_account_activation_reset(self):
        """
        Test for testing the account creation activation functionality.
        """
        # print("account activation test, debug status: ", settings.DEBUG)
        url = "/users/create/"
        # url = "/users/activate/"
        url2 = settings.USER_ACTIVATION_URL_FRONT

        # creating user that needs to be activated
        data = {
            "first_name": "t",
            "last_name": "t",
            "email": "t@turku.fi",
            "phone_number": "5555",
            "password": "1234",
            "address": "test12",
            "zip_code": "12552",
            "city": "TESTIKAUPUNKI",
        }
        response = self.client.post(url, data, content_type="application/json")

        # testing that email was sent
        self.assertEqual(
            len(mail.outbox),
            1,
            "mail should have been sent in user creattion",
        )

        # checking that the user is not active
        user = CustomUser.objects.get(username="t@turku.fi")
        self.assertFalse(user.is_active, "User shouldnt be activee after creation")

        # should not be able to login
        url = "/users/login/"
        data = {
            "username": "t@turku.fi",
            "password": "1234",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            204, response.status_code, "shouldnt be able to login wihtout being active"
        )

        url = "/users/activate/"

        # checking that te front url is in the  activation mail
        self.assertTrue(
            (settings.USER_ACTIVATION_URL_FRONT in mail.outbox[0].body),
            "front address should be in activation mail",
        )

        # grabbing the link from the email that was sent, and putting it into form that can be used with test
        end_part_of_email_link = mail.outbox[0].body.split(url2)
        the_parameters = end_part_of_email_link[1].split("/")

        data = {
            "uid": "a",
            "token": "a",
        }

        # wrong kind of encoded uid
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            204,
            "should get wrongly stuff with wrong uid",
        )

        # testataan ei oikealla uidllä jota ei olemassa
        uid = urlsafe_base64_encode(force_bytes(-1))
        data = {
            "uid": uid,
            "token": "a",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            204,
            "should get wrongly stuff with non existant uid",
        )

        data = {
            "uid": the_parameters[0],
            "token": "a",
        }
        # testing response with non  valid token
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            response.status_code,
            204,
            "should get wrongly stuff with wrong token",
        )

        # par 0 should be encoded uid, par 1 the token for reset
        data = {
            "uid": the_parameters[0],
            "token": the_parameters[1],
        }
        response = self.client.post(url, data, content_type="application/json")

        # checking for right statuts code on righ values
        self.assertEqual(
            200,
            response.status_code,
            "should get 200 response on succesfull activation",
        )

        # active status check
        user = CustomUser.objects.get(username="t@turku.fi")
        self.assertTrue(user.is_active, "user should be active")

        # should be able to login now
        url = "/users/login/"
        data = {
            "username": "t@turku.fi",
            "password": "1234",
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(
            200, response.status_code, "should be able to login when active now"
        )
