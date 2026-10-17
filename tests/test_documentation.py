import re, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
INDEX = ["PROJECT_INDEX.md","AGENTS.md","docs/HR.md","docs/ENGINEERING.md","docs/INTEGRATION.md","docs/ART.md","docs/R_AND_D.md"]
class DepartmentContinuity(unittest.TestCase):
    def test_all_department_records_exist(self):
        for p in INDEX:
            with self.subTest(p=p): self.assertTrue((ROOT/p).is_file())
    def test_each_record_nonempty(self):
        for p in INDEX:
            with self.subTest(p=p): self.assertGreater(len((ROOT/p).read_text().strip()),60)
    def test_internal_markdown_links_resolve(self):
        for p in INDEX:
            file=ROOT/p
            for dest in re.findall(r"\[[^]]+\]\(([^)]+)\)",file.read_text()):
                if dest.startswith(("http:","https:","#")): continue
                with self.subTest(source=p,target=dest):
                    self.assertTrue((file.parent/dest.split("#",1)[0]).is_file())
    def test_every_department_linked_from_index(self):
        index=(ROOT/"PROJECT_INDEX.md").read_text()
        for p in INDEX[2:]:
            with self.subTest(doc=p): self.assertIn(f"({p})", index)
