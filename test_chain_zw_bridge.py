import unittest
from pathlib import Path
from chain_zw_bridge import parse_zw,run_zw
HERE=Path(__file__).resolve().parent

class TestZWBridge(unittest.TestCase):
    def test_real_demo(self):
        original=(HERE/'chain_zw_demo.zw').read_text()
        input_copy=original[:]
        out=parse_zw(run_zw(original))
        self.assertEqual(original,input_copy)
        self.assertEqual(len(out['accepted']),6)
        ts={t['id']:t for t in out['targets']}
        self.assertEqual((ts['wet_foe']['state'],ts['wet_foe']['elements']), ('Boil',['water','fire']))
        self.assertTrue(76.6<=ts['wet_foe']['hp']<=76.8)  # 77 minus the 2nd-hit bonus (2-4% of 10)
        self.assertEqual((ts['resistant_foe']['hp'],ts['resistant_foe']['elements']), (860.0,['spirit']))
        self.assertEqual((ts['char_foe']['state'],ts['char_foe']['closed']), ('Char',True))
    def test_third_hit(self):
        p='{combat_chain_request {version 1} {targets [{target {id foe} {hp 10}}]} {hits [{hit {id a} {target foe} {primary true} {damage_fire 1}} {hit {id b} {target foe} {primary true} {damage_water 1}} {hit {id c} {target foe} {primary true} {damage_ice 1}}]}}'
        foe=parse_zw(run_zw(p))['targets'][0]
        self.assertFalse(foe['closed'])  # no hit limit
        self.assertEqual(foe['elements'],['fire','water','ice'])
    def test_ongoing_final_infliction(self):
        # Fire leaves 50 ongoing; Water replaces it: 10 + 10 + 50*1.02, standard 0 = no bonus roll.
        p='{combat_chain_request {version 1} {targets [{target {id foe} {hp 100}}]} {hits [{hit {id a} {target foe} {primary true} {damage_fire 10} {ongoing 50}} {hit {id b} {target foe} {primary true} {damage_water 10} {ongoing 20} {standard 0}}]}}'
        foe=parse_zw(run_zw(p))['targets'][0]
        self.assertAlmostEqual(foe['hp'],100-20-51)
        self.assertEqual((foe['state'],foe['ongoing']),('Steam',20.0))
    def test_reject_bad_ongoing(self):
        p='{combat_chain_request {version 1} {targets [{target {id foe} {hp 1}}]} {hits [{hit {id a} {target foe} {primary true} {damage_fire 1} {ongoing -1}}]}}'
        with self.assertRaises(ValueError):run_zw(p)
    def test_unapproved_pair(self):
        p='{combat_chain_request {version 1} {targets [{target {id foe} {hp 10}}]} {hits [{hit {id a} {target foe} {primary true} {damage_moon 1}} {hit {id b} {target foe} {primary true} {damage_shadow 1}}]}}'
        data=parse_zw(run_zw(p))
        self.assertEqual(data['targets'][0]['elements'],['moon','shadow'])
        self.assertIn('unauthored',data['alerts'][0])
    def test_reject_duplicate_target(self):
        p='{combat_chain_request {version 1} {targets [{target {id a} {hp 1}} {target {id a} {hp 1}}]} {hits []}}'
        with self.assertRaises(ValueError):run_zw(p)
    def test_reject_bad_syntax(self):
        with self.assertRaises(ValueError):run_zw('{combat_chain_request {version 1}')

if __name__=='__main__':unittest.main(verbosity=2)
