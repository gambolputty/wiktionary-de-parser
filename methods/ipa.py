def init(title, text, record):
    match_ipa_p = re.search(r'{{Aussprache}}((?:\n.+)+)', text)
    found_ipa = []
    if match_ipa_p:
        lines = match_ipa_p.group(1).splitlines()
        for line in lines:
            if not line:
                continue

            if not re.match(r'^:?(?:\[\d+\] )?{{IPA}} ', line):
                continue
            # erlaube nur bestimmt Trennung von IPAs
            split = re.split(r"({{Lautschrift\|[^}]+}})", line)
            for s in split[1:]:
                s = s.strip()
                if not s:
                    continue
                match_ipa = re.match(r'{{Lautschrift\|([^}]+)}}', s)
                if match_ipa:
                    found_ipa.append(match_ipa.group(1))
                    continue
                if s not in allowed_sep:
                    break
    # gleiche mit Reim-Feld ab, falls vorhanden
    reim_match = re.search(r'{{Reim\|([^}|]+)(?:\|[^}]+)*}}', text)
    if reim_match:
        r = reim_match.group(1)
        m = [x for x in found_ipa if x.endswith(r)]
        if m:
            return m[0]
    if found_ipa:
        return found_ipa[0]
    return False
