from django.test import TestCase
from pokemon.models import Nature, Species, Pokemon, Type, Move, Ability


class PokemonTestCase(TestCase):
    def setUp(self):
        self.nature1 = Nature.objects.create(name="lax")
        self.nature2 = Nature.objects.create(name="quirky")
        self.ability1 = Ability.objects.create(name="stench")
        self.type1 = Type.objects.create(name="normal")
        self.type2 = Type.objects.create(name="flying")
        self.type3 = Type.objects.create(name="psychic")
        self.species1 = Species.objects.create(
            name="snorlax",
            type1=self.type1,
            id=1,
            hp=50,
            attack=50,
            special_attack=50,
            defense=50,
            special_defense=50,
            speed=50
        )
        self.species2 = Species.objects.create(
            name="ho-oh",
            type1=self.type2,
            id=2,
            hp=50,
            attack=50,
            special_attack=50,
            defense=50,
            special_defense=50,
            speed=50
        )
        self.attacker = Pokemon.objects.create(species=self.species1, ability=self.ability1, nature=self.nature1)
        self.defender = Pokemon.objects.create(species=self.species1, ability=self.ability1, nature=self.nature1)

    def test_tackle(self):
        """Testing implementation of tackle move"""
        move = Move.objects.create(
            name="tackle",
            power=40,
            priority=0,
            accuracy=100,
            pp=35,
            type=self.type1,
            damage_class=Move.DamageClass.PHYSICAL,
            drain=0,
            recoil=0
        )
        damage = move.max_damage(attacker=self.attacker, defender=self.defender)
        self.assertEqual(damage, 28)

    def test_hyper_beam(self):
        """Testing implementation of hyper beam move"""
        move = Move.objects.create(
            name="hyper-beam",
            power=150,
            priority=0,
            accuracy=90,
            pp=5,
            type=self.type1,
            damage_class=Move.DamageClass.SPECIAL,
            drain=0,
            recoil=0
        )
        damage = move.max_damage(attacker=self.attacker, defender=self.defender)
        self.assertEqual(damage, 52)

    def test_future_sight(self):
        """Testing implementation of future sight move"""
        move = Move.objects.create(
            name="future-sight",
            power=120,
            priority=0,
            accuracy=100,
            pp=10,
            type=self.type3,
            damage_class=Move.DamageClass.SPECIAL,
            drain=0,
            recoil=0
        )
        damage = move.max_damage(attacker=self.attacker, defender=self.defender)
        self.assertEqual(damage, 28)

    def test_zero_power_move(self):
        """Zero power moves should do zero damage."""
        move = Move.objects.create(
            name='swords-dance',
            power=0,
            priority=0,
            accuracy=100,
            pp=10,
            type=self.type3,
            damage_class=Move.DamageClass.STATUS,
            drain=0,
            recoil=0
        )
        damage = move.max_damage(attacker=self.attacker, defender=self.defender)
        self.assertEqual(damage, 0)
