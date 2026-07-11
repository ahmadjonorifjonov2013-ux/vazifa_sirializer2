from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Category, Product


class ProductSerializer(serializers.ModelSerializer):
    # 4-band: validators + UniqueValidator (kamida 1 maydon)
    title = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=Product.objects.all(),
                message="Bu nom band",
            )
        ]
    )

    # 6-band: read_only maydon — javobda bor, kiritib bo'lmaydi
    created = serializers.DateTimeField(read_only=True)

    # 6-band: write_only maydon — kiritiladi, javobda ko'rinmaydi
    secret_code = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )

    # 7-band: SerializerMethodField — modelda yo'q, hisoblanadigan maydon
    category_name = serializers.SerializerMethodField()

    # category — oddiy holatda ID (int) qabul qiladi (masalan category: 1),
    # lekin nested yaratishda dict ({"name": ..., "city": ...}) ham qabul qiladi.
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "price",
            "sale_price",
            "year",
            "category",
            "category_name",
            "secret_code",
            "created",
        ]

    def get_category_name(self, obj):
        return obj.category.name if obj.category_id else None

    # ---------- 3-band: maydon validatsiyasi (validate_<field>) ----------
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Narx 0 dan katta bo'lsin")
        return value

    def validate_year(self, value):
        if not (1900 <= value <= 2026):
            raise serializers.ValidationError("Yil 1900–2026 orasida bo'lsin")
        return value

    # ---------- 5-band: obyekt darajasidagi validatsiya ----------
    def validate(self, data):
        price = data.get("price", getattr(self.instance, "price", None))
        sale_price = data.get("sale_price", getattr(self.instance, "sale_price", None))
        if price is not None and sale_price is not None and sale_price > price:
            raise serializers.ValidationError(
                "Chegirma narxi asl narxdan katta bo'lmasin"
            )
        return data

    # ---------- category maydoniga dict (nested) yuborilsa qabul qilish ----------
    def to_internal_value(self, data):
        # Agar category maydoni {"name": ..., "city": ...} ko'rinishida kelsa,
        # PrimaryKeyRelatedField uni tushunmaydi — shuning uchun vaqtincha
        # olib qo'yib, keyin create() ichida qo'lda ishlatamiz.
        category_raw = data.get("category")
        self._nested_category_data = None
        if isinstance(category_raw, dict):
            self._nested_category_data = category_raw
            data = data.copy()
            data["category"] = None
        return super().to_internal_value(data)

    # ---------- 9-band: nested create() override ----------
    def create(self, validated_data):
        nested_category_data = getattr(self, "_nested_category_data", None)
        if nested_category_data:
            category, _ = Category.objects.get_or_create(
                name=nested_category_data.get("name"),
                defaults={"city": nested_category_data.get("city", "")},
            )
            validated_data["category"] = category
        return Product.objects.create(**validated_data)

    # ---------- (ixtiyoriy, +10 ball) nested update() override ----------
    def update(self, instance, validated_data):
        nested_category_data = getattr(self, "_nested_category_data", None)
        if nested_category_data:
            category, _ = Category.objects.get_or_create(
                name=nested_category_data.get("name"),
                defaults={"city": nested_category_data.get("city", "")},
            )
            validated_data["category"] = category

        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class CategorySerializer(serializers.ModelSerializer):
    # 8-band: nested serializer — ota ichida bola ro'yxati (many=True)
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "city", "products"]
