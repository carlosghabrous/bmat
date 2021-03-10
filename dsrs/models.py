from django.db import models


class Territory(models.Model):
    name = models.CharField(max_length=48)
    code_2 = models.CharField(max_length=2)
    code_3 = models.CharField(max_length=3)
    local_currency = models.ForeignKey(
        "Currency", related_name="territories", on_delete=models.CASCADE
    )

    class Meta:
        '''A unique constraint has been added in order to prevent the same territory to be inserted more than once'''
        db_table = "territory"
        verbose_name = "territory"
        verbose_name_plural = "territories"
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(fields=['name', 'code_2'], name='territory_name_code_unique'),
        ]



class Currency(models.Model):
    '''A unique constraint has been added in order to prevent the same currency to be inserted more than once'''
    name = models.CharField(max_length=48)
    symbol = models.CharField(max_length=4)
    code = models.CharField(max_length=3)

    class Meta:
        db_table = "currency"
        verbose_name = "currency"
        verbose_name_plural = "currencies"
        constraints = [
            models.UniqueConstraint(fields=['name', 'code'], name='currency_name_code_unique'),
        ]


class DSR(models.Model):
    class Meta:
        '''A unique constraint has been added in order to prevent the same DSR to be inserted more than once'''
        db_table = "dsr"
        constraints = [
            models.UniqueConstraint(fields=['path', 'period_start', 'period_end', 'territory', 'currency'],
                                    name='dsr_unique_constraint')
        ]

    STATUS_ALL = (
        ("failed", "FAILED"),
        ("ingested", "INGESTED"),
    )

    path = models.CharField(max_length=256)
    period_start = models.DateField(null=False)
    period_end = models.DateField(null=False)

    status = models.CharField(
        choices=STATUS_ALL, default=STATUS_ALL[0][0], max_length=48
    )

    territory = models.ForeignKey(
        Territory, related_name="dsrs", on_delete=models.CASCADE
    )
    currency = models.ForeignKey(
        Currency, related_name="dsrs", on_delete=models.CASCADE
    )

class DSP(models.Model):
    '''FROM CARLOS: The DSP table models the information contained in the tsv.gz files.

    The maximum lengths for the different fields have been chosen arbitrarily taking
    into account the samples provided. The revenue field has been setup as a 'decimal'
    instead of a 'float' type, so that there are no issues with loss of precission.

    The field dsp_id has been choosen as the primary key, since it seems to be unique.
    Also, this would prevent to insert twice the same record on the database for a given 
    DSR.

    The table must be linked to the 'dsr' table, so that the query specified in the API model,
    /resources/percentile/{number}, can be filtered by the optional parameters 'territory',
    'period_start' and 'period_end'. This has been achieved via the column 'dsr_id.'
    The cascade policy on deleting has not been implemented to preserve a 'dsr' even if a 'dsp'
    is deleted, since there might be more 'dsps' associated with it.'''
    class Meta:
        db_table = "dsp"

    dsp_id   = models.CharField(max_length=128, primary_key=True)
    title    = models.CharField(max_length=128)
    artists  = models.CharField(max_length=256)
    isrc     = models.CharField(max_length=12)
    usages   = models.PositiveIntegerField()
    revenue  = models.DecimalField(max_digits=40, decimal_places=19)
    dsr_id   = models.ForeignKey(DSR, related_name="dsps", on_delete=models.DO_NOTHING)
