# from space.models import Product, Account
# from rest_framework import serializers

# class PostSerializer(serializers.HyperlinkedModelSerializer):
# 	class Meta:
# 		model = Product
# 		fields = ('price', 'description')


# class AccountSerializer(serializers.HyperlinkedModelSerializer):
# 	class Meta:
# 		model = Account
# 		fields = ('id_name', 'display_name', 'phone')


from rest_framework import serializers
from space.models import Product, ProductReact

class ProductAPI(serializers.ModelSerializer):
	class Meta:
		model = Product

		fields = ('title', 'description')


class ProductListAPI(serializers.ModelSerializer):
	class Meta:
		model = ProductReact
		fields = ('__all__')
		