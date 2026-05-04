#!/usr/bin/env python3
"""
필드 매핑 파일 생성 도구

분석된 결과를 기반으로 Goose가 사용할 수 있는 매핑 파일을 생성합니다.
"""

import json
import os
import sys
from typing import Dict, Any, List


class MappingGenerator:
    def __init__(self):
        self.mapping = {
            'project': 'YOUR_PROJECT_NAME',
            'issue_types': {},
            'traceability': {},
            'status': {},
            'content': {}
        }

    def load_analysis(self, file_path: str) -> Dict[str, Any]:
        """분석 결과 파일 로드"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def infer_field_categories(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """필드 카테고리 추론"""
        fields = analysis.get('fields', {})
        field_defs = analysis.get('field_definitions', {})

        categorized = {
            'issue_type': None,
            'parent_ticket': None,
            'sub_tickets': None,
            'status': {},
            'content': {},
            'other': []
        }

        for field_id, field_info in fields.items():
            name = field_info['name'].lower()
            field_type = field_info.get('type', 'unknown')

            # 이슈 타입
            if 'issue type' in name or 'type' in name and 'issue' in name:
                categorized['issue_type'] = field_id

            # 부모 티켓
            elif 'parent' in name or 'epic' in name or 'linked issue' in name:
                if field_type == 'array':
                    categorized['sub_tickets'] = field_id
                else:
                    categorized['parent_ticket'] = field_id

            # 상태
            elif 'status' in name or 'progression' in name:
                allowed = field_defs.get(field_id, {}).get('allowed_values')
                if allowed:
                    categorized['status'][field_id] = {
                        'name': field_info['name'],
                        'options': {self._slugify(v): v for v in allowed}
                    }

            # 내용
            elif 'description' in name or 'content' in name or 'document' in name:
                categorized['content'][field_id] = {
                    'name': field_info['name'],
                    'type': field_type
                }

            else:
                categorized['other'].append({
                    'id': field_id,
                    'name': field_info['name'],
                    'type': field_type,
                    'has_value': field_info.get('has_value', False)
                })

        return categorized

    def _slugify(self, text: str) -> str:
        """텍스트를 슬러그로 변환"""
        return text.lower().replace(' ', '_').replace('-', '_')

    def generate_mapping(self, analysis_file: str) -> Dict[str, Any]:
        """매핑 파일 생성"""
        analysis = self.load_analysis(analysis_file)
        ticket = analysis.get('ticket', {})
        issue_type = ticket.get('issuetype', 'Unknown')

        # 카테고리 추론
        categorized = self.infer_field_categories(analysis)

        # 매핑 구성
        self.mapping['project'] = ticket['id'].split('-')[0]
        self.mapping['current_analysis_type'] = issue_type

        if categorized['issue_type']:
            self.mapping['issue_types'][self._slugify(issue_type)] = {
                'name': issue_type,
                'field_id': categorized['issue_type']
            }

        if categorized['parent_ticket']:
            self.mapping['traceability']['parent_ticket'] = {
                'field_id': categorized['parent_ticket']
            }

        if categorized['sub_tickets']:
            self.mapping['traceability']['sub_tickets'] = {
                'field_id': categorized['sub_tickets'],
                'type': 'array_issue'
            }

        self.mapping['status'] = categorized['status']
        self.mapping['content'] = categorized['content']

        if categorized['other']:
            self.mapping['uncategorized_fields'] = categorized['other']

        return self.mapping

    def save_mapping(self, output_file: str):
        """매핑 파일 저장"""
        # 주석 추가를 위한 YAML 스타일 정리
        output = f"# Jira Field Mapping for {self.mapping['project']}\n"
        output += f"# Generated from analysis\n\n"

        output += f"project: {self.mapping['project']}\n\n"

        output += "# 이슈 타입 매핑\n"
        output += "issue_types:\n"
        for key, value in self.mapping.get('issue_types', {}).items():
            output += f"  {key}:\n"
            output += f"    name: {value['name']}\n"
            output += f"    field_id: {value['field_id']}\n"

        output += "\n# 추적성 필드\n"
        output += "traceability:\n"
        for key, value in self.mapping.get('traceability', {}).items():
            output += f"  {key}:\n"
            output += f"    field_id: {value['field_id']}\n"
            if 'type' in value:
                output += f"    type: {value['type']}\n"

        output += "\n# 상태 필드\n"
        output += "status:\n"
        for field_id, value in self.mapping.get('status', {}).items():
            output += f"  {field_id}:\n"
            output += f"    name: {value['name']}\n"
            output += f"    options:\n"
            for opt_key, opt_value in value['options'].items():
                output += f"      {opt_key}: \"{opt_value}\"\n"

        output += "\n# 내용 필드\n"
        output += "content:\n"
        for field_id, value in self.mapping.get('content', {}).items():
            output += f"  {field_id}:\n"
            output += f"    name: {value['name']}\n"
            output += f"    type: {value['type']}\n"

        if 'uncategorized_fields' in self.mapping:
            output += "\n# 분류되지 않은 필드 (검토 필요)\n"
            output += "uncategorized:\n"
            for field in self.mapping['uncategorized_fields']:
                output += f"  - id: {field['id']}\n"
                output += f"    name: {field['name']}\n"
                output += f"    type: {field['type']}\n"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate-mapping.py <analysis-file.json>")
        print("Example:")
        print("  python generate-mapping.py ticket_analysis_PROJ-123.json")
        sys.exit(1)

    analysis_file = sys.argv[1]

    if not os.path.exists(analysis_file):
        print(f"Error: File not found: {analysis_file}")
        sys.exit(1)

    generator = MappingGenerator()

    try:
        mapping = generator.generate_mapping(analysis_file)

        output_file = "field_mapping.yml"
        generator.save_mapping(output_file)

        print("\n" + "="*50)
        print("MAPPING GENERATION COMPLETE")
        print("="*50)
        print(f"Project: {mapping['project']}")
        print(f"Type analyzed: {mapping.get('current_analysis_type', 'Unknown')}")
        print(f"Issue types: {len(mapping.get('issue_types', {}))}")
        print(f"Traceability fields: {len(mapping.get('traceability', {}))}")
        print(f"Status fields: {len(mapping.get('status', {}))}")
        print(f"Content fields: {len(mapping.get('content', {}))}")
        if 'uncategorized_fields' in mapping:
            print(f"Uncategorized: {len(mapping['uncategorized_fields'])}")

        print(f"\nMapping saved to: {output_file}")
        print("\nPlease review and update the mapping file as needed.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
