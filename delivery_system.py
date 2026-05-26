import sys
from math import sqrt
from pathlib import Path


class JsonParser:
    def __init__(self, raw):
        self.raw = raw
        self.pos = 0

    def run(self):
        result = self._next_value()
        self._consume_whitespace()
        return result

    def _next_value(self):
        self._consume_whitespace()
        c = self.raw[self.pos]

        if c == '{':
            return self._parse_object()
        if c == '[':
            return self._parse_array()
        if c == '"':
            return self._parse_string()
        if c in '-0123456789':
            return self._parse_number()
        if self.raw.startswith('true', self.pos):
            self.pos += 4
            return True
        if self.raw.startswith('false', self.pos):
            self.pos += 5
            return False
        if self.raw.startswith('null', self.pos):
            self.pos += 4
            return None

        raise SyntaxError(f"Unexpected character '{c}' at position {self.pos}")

    def _parse_object(self):
        obj = {}
        self.pos += 1
        self._consume_whitespace()

        if self.raw[self.pos] == '}':
            self.pos += 1
            return obj

        while True:
            self._consume_whitespace()
            key = self._parse_string()
            self._consume_whitespace()

            if self.raw[self.pos] == ':':
                self.pos += 1

            val = self._next_value()
            obj[key] = val
            self._consume_whitespace()

            if self.raw[self.pos] == '}':
                self.pos += 1
                break
            if self.raw[self.pos] == ',':
                self.pos += 1

        return obj

    def _parse_array(self):
        items = []
        self.pos += 1
        self._consume_whitespace()

        if self.raw[self.pos] == ']':
            self.pos += 1
            return items

        while True:
            val = self._next_value()
            items.append(val)
            self._consume_whitespace()

            if self.raw[self.pos] == ']':
                self.pos += 1
                break
            if self.raw[self.pos] == ',':
                self.pos += 1

        return items

    def _parse_string(self):
        self.pos += 1
        chars = []

        while self.pos < len(self.raw):
            c = self.raw[self.pos]

            if c == '"':
                self.pos += 1
                return ''.join(chars)

            if c == '\\':
                self.pos += 1
                if self.pos < len(self.raw):
                    chars.append(self.raw[self.pos])
                    self.pos += 1
                continue

            chars.append(c)
            self.pos += 1

        return ''.join(chars)

    def _parse_number(self):
        start = self.pos

        if self.raw[self.pos] == '-':
            self.pos += 1

        while self.pos < len(self.raw) and self.raw[self.pos].isdigit():
            self.pos += 1

        is_float = False
        if self.pos < len(self.raw) and self.raw[self.pos] == '.':
            is_float = True
            self.pos += 1
            while self.pos < len(self.raw) and self.raw[self.pos].isdigit():
                self.pos += 1

        token = self.raw[start:self.pos]
        return float(token) if is_float else int(token)

    def _consume_whitespace(self):
        while self.pos < len(self.raw) and self.raw[self.pos] in ' \n\t\r':
            self.pos += 1


def read_json(filepath):
    content = Path(filepath).read_text(encoding='utf-8')
    return JsonParser(content).run()


def normalize_warehouses(data):
    if isinstance(data, dict):
        return data
    return {entry['id']: entry['location'] for entry in data}


def normalize_agents(data):
    if isinstance(data, dict):
        return data
    return {entry['id']: entry['location'] for entry in data}


def normalize_packages(data):
    cleaned = []
    for pkg in data:
        cleaned.append({
            'id': pkg['id'],
            'warehouse': pkg.get('warehouse') or pkg.get('warehouse_id'),
            'destination': pkg['destination']
        })
    return cleaned


def euclidean(a, b):
    return sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def assign_deliveries(warehouses, agents, packages):
    stats = {
        aid: {'packages_delivered': [], 'total_distance': 0.0}
        for aid in agents
    }

    for pkg in packages:
        wh_loc = warehouses[pkg['warehouse']]
        dest = pkg['destination']

        nearest_agent = min(agents, key=lambda aid: euclidean(agents[aid], wh_loc))
        travel = euclidean(agents[nearest_agent], wh_loc) + euclidean(wh_loc, dest)

        stats[nearest_agent]['packages_delivered'].append(pkg['id'])
        stats[nearest_agent]['total_distance'] += travel

    summary = {}
    top_agent = ''
    top_score = None

    for aid, info in stats.items():
        n = len(info['packages_delivered'])
        dist = round(info['total_distance'], 2)
        eff = round(dist / n, 2) if n > 0 else 0.0

        summary[aid] = {
            'packages_delivered': info['packages_delivered'],
            'package_count': n,
            'total_distance': dist,
            'efficiency': eff
        }

        if n > 0 and (top_score is None or eff < top_score):
            top_score = eff
            top_agent = aid

    return {
        'agents': summary,
        'best_agent': top_agent,
        'total_packages': len(packages)
    }


def to_json_string(val, depth=0):
    pad = '  ' * depth
    inner = '  ' * (depth + 1)

    if isinstance(val, dict):
        if not val:
            return '{}'
        entries = []
        keys = list(val.keys())
        for i, k in enumerate(keys):
            sep = ',' if i < len(keys) - 1 else ''
            entries.append(f'{inner}"{k}": {to_json_string(val[k], depth + 1)}{sep}')
        return '{\n' + '\n'.join(entries) + '\n' + pad + '}'

    if isinstance(val, list):
        if not val:
            return '[]'
        entries = []
        for i, item in enumerate(val):
            sep = ',' if i < len(val) - 1 else ''
            entries.append(f'{inner}{to_json_string(item, depth + 1)}{sep}')
        return '[\n' + '\n'.join(entries) + '\n' + pad + ']'

    if isinstance(val, bool):
        return 'true' if val else 'false'

    if val is None:
        return 'null'

    if isinstance(val, str):
        return f'"{val}"'

    return str(val)


def generate_report(input_path, output_path):
    raw = read_json(input_path)

    warehouses = normalize_warehouses(raw['warehouses'])
    agents = normalize_agents(raw['agents'])
    packages = normalize_packages(raw['packages'])

    report = assign_deliveries(warehouses, agents, packages)

    Path(output_path).write_text(to_json_string(report), encoding='utf-8')


def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'base_case.json'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'report.json'

    generate_report(input_file, output_file)
    print(f'Done! Output written to: {output_file}')


if __name__ == '__main__':
    main()