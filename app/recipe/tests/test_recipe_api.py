from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from mainapp.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse("recipe:recipe-detail", args=[recipe_id])
    # it will look like this: .../recipe/recipes/1


def create_user(**params):
    return get_user_model().objects.create_user(**params)


# in tests we can create our own recipes by just overriding default vals
def create_sample_recipe(user, **params):
    """Create and retrieve a sample recipe"""
    defaults = {
        "title": "Sample recipe",
        "time_minutes": 10,
        "price": 5.99
    }
    defaults.update(params)
    # here we can assign any params to this function and it will by default
    # update those values which are in defaults or it(defaults) will
    # create/accept other params and save dictionary.

    return Recipe.objects.create(user=user, **defaults)


def create_sample_tag(user, name="Lunch"):
    """Create and retrieve a sample tag"""
    return Tag.objects.create(user=user, name=name)


def create_sample_ingredient(user, name="Sugar"):
    """Create and retrieve a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


class PublicRecipesApiTests(TestCase):
    """Test publicly available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test login is required for retrieving ingredients"""
        response = self.client.get(RECIPES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipesApiTests(TestCase):
    """Test the authorized user ingredients"""

    def setUp(self):
        self.user = create_user(email="testt@gmail.com", password="Test1234")
        self.client = APIClient()

        self.client.force_authenticate(self.user)

    def test_retrieve_recipe_list(self):
        """Test if authenticated users can retrieve/see ingredients that
           he/she created"""

        create_sample_recipe(user=self.user)
        create_sample_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all()  # .order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

        # here the var serializer refers to RecipeSerializer, meaning that
        # it will show the data that is stored in table in database.
        # ie. >>> print(repr(serializer))
        # RecipeSerializer():
        #   id = IntegerField(label='ID', read_only=True)
        #   title = CharField(max_length=255)
        #   ingredients = PrimaryKeyRelatedField(
        #                 queryset=Ingredient.objects.all())
        #   ...

    def test_assigned_recipes_limited_user(self):
        """Test if the authenticated(logged in) user gets only
           assigned recipes to his/her user. Or with other words,
           recipes returned are for the current authencticated user"""

        user2 = create_user(email='testt2@gmail.com', password='Test12345')

        create_sample_recipe(user=user2)
        create_sample_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing recipe detail (accessing that endpoint)"""
        recipe = create_sample_recipe(user=self.user)

        # After defining the Many to many relationship of models
        # (Tag, Ingredient, Recipe) in serializer and models, we can now
        # add tags, ingredients like this:
        recipe.tags.add(create_sample_tag(user=self.user))
        recipe.ingredients.add(create_sample_ingredient(user=self.user))
        # here, we are adding tag and ingredient to current created recipe

        url = detail_url(recipe.id)
        response = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.data, serializer.data)
