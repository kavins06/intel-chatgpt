import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/'skills/intel/scripts'
sys.path.insert(0,str(ROOT/'scripts'))
from package import build
from distribution import package_paths


def run(script,*args):
    env=dict(os.environ)
    env.pop('INTEL_SOURCE_DIR',None)
    return subprocess.run([sys.executable,str(SCRIPTS/script),*map(str,args)],capture_output=True,text=True,env=env)


class SourceBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.directory=Path(self.temp.name)

    def test_missing_source_is_not_negative_evidence(self):
        result=run('source_library.py','--data-dir',self.directory,'search','risk limits','--source','S16')
        self.assertEqual(result.returncode,0,result.stderr)
        data=json.loads(result.stdout)
        self.assertEqual(data['status'],'no_local_sources')
        self.assertEqual(data['searched_sources'],0)
        self.assertIn('S16',data['unavailable_sources'])
        result=run('source_library.py','--data-dir',self.directory,'read','S16','--pages','1')
        self.assertEqual(result.returncode,2)

    def test_local_ingest_search_read_and_no_overwrite(self):
        fixture=self.directory/'pages.json'
        fixture.write_text(json.dumps([{'page':1,'text':'Synthetic case: risk limits were monitored and tested.','method':'synthetic fixture'}]))
        data_dir=self.directory/'index'
        imported=run('import_source.py','U01','--pages-json',fixture,'--title','Synthetic test source','--data-dir',data_dir)
        self.assertEqual(imported.returncode,0,imported.stderr)
        result=run('source_library.py','--data-dir',data_dir,'search','risk limits','--source','U01')
        data=json.loads(result.stdout)
        self.assertEqual(data['searched_sources'],1)
        self.assertEqual(data['results'][0]['pdf_page'],1)
        result=run('source_library.py','--data-dir',data_dir,'read','U01','--pages','1')
        self.assertIn('Synthetic case',json.loads(result.stdout)['pages'][0]['text'])
        duplicate=run('import_source.py','U01','--pages-json',fixture,'--data-dir',data_dir)
        self.assertEqual(duplicate.returncode,2)
        reserved=run('import_source.py','S16','--pages-json',fixture,'--data-dir',data_dir)
        self.assertEqual(reserved.returncode,2)
        bounds=run('source_library.py','--data-dir',data_dir,'read','U01','--pages','2')
        self.assertEqual(bounds.returncode,2)

    def test_local_index_cannot_escape_source_directory(self):
        index=[{'id':'U01','title':'Malformed fixture','pages':1,'page_data':'../outside.json','tags':[]}]
        (self.directory/'source-index.json').write_text(json.dumps(index))
        result=run('source_library.py','--data-dir',self.directory,'read','U01','--pages','1')
        self.assertEqual(result.returncode,2)
        self.assertIn('escapes',result.stderr)

    def test_public_archive_excludes_private_material_and_is_reproducible(self):
        first=self.directory/'first.zip';second=self.directory/'second.zip'
        build(ROOT,first);build(ROOT,second)
        self.assertEqual(hashlib.sha256(first.read_bytes()).digest(),hashlib.sha256(second.read_bytes()).digest())
        with zipfile.ZipFile(first) as archive:
            self.assertEqual(set(archive.namelist()),{'intel/'+x for x in package_paths()})
            self.assertTrue(all(not x.endswith(('.pdf','.PDF')) and '/source-text/' not in x and '/local-sources/' not in x for x in archive.namelist()))
            self.assertEqual(sum(x.endswith('/SKILL.md') for x in archive.namelist()),10)
            manifest=json.loads(archive.read('intel/plugin.json'))
            interface=manifest['extensions']['com.openai']['interface']
            for key in ('logo','composerIcon'):
                asset=interface[key].removeprefix('./')
                self.assertEqual(archive.read('intel/'+asset),(ROOT/asset).read_bytes())
            marketplace=json.loads(archive.read('intel/.agents/plugins/marketplace.json'))
            source=marketplace['plugins'][0]['source']['path']
            self.assertIn('intel/'+str(Path(source)/'plugin.json'),archive.namelist())
            self.assertIsNone(archive.testzip())


class EvidenceTests(unittest.TestCase):
    def test_broken_sources_and_forecast_scale_are_rejected(self):
        spec=importlib.util.spec_from_file_location('checker',SCRIPTS/'check_evidence.py')
        checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
        valid={'question':'Synthetic decision','as_of':'2026-09-27','sources':[{'id':'E1','title':'Fixture','locator':'p. 1','family':'fixture'}], 'claims':[{'id':'C1','text':'Synthetic attributed claim','kind':'attributed_claim','evidence':[{'source_id':'E1','locator':'p. 1'}]}], 'forecasts':[{'id':'F1','question':'Synthetic binary event','deadline':'2026-10-01','resolution_rule':'Fixture outcome','basis':'Illustration only','probability':0.8,'outcome':1}]}
        result=checker.check(valid)
        self.assertTrue(result['valid_structure'])
        self.assertAlmostEqual(result['mean_brier_score'],0.04)
        bad=copy.deepcopy(valid);bad['claims'][0]['evidence'][0]['source_id']='missing'
        self.assertFalse(checker.check(bad)['valid_structure'])
        bad=copy.deepcopy(valid);bad['forecasts'][0]['probability']=80
        self.assertFalse(checker.check(bad)['valid_structure'])


if __name__=='__main__':unittest.main()
