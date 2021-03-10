from rest_framework import serializers

from . import models


class TerritorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Territory
        fields = (
            "name",
            "code_2",
        )


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Currency
        fields = (
            "name",
            "code",
        )


class DSRSerializer(serializers.ModelSerializer):
    territory = TerritorySerializer()
    currency = CurrencySerializer()

    class Meta:
        model = models.DSR
        fields = (
            "id",
            "path",
            "period_start",
            "period_end",
            "status",
            "territory",
            "currency",
        )

class DSPSerializer(serializers.ModelSerializer):
    '''FROM CARLOS: Added basic serializer for the DSP model'''
    dsr_id = DSRSerializer()

    class Meta:
        model = models.DSP
        fields = (
            "dsp_id",
            "title",
            "artists",
            "isrc",
            "usages",
            "revenue",
            "dsr_id",
        )
