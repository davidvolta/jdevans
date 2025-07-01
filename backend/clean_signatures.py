import json

with open('poems.json', 'r') as f:
    poems = json.load(f)

changed = False
for poem in poems:
    if 'signature' in poem:
        new_sig = poem['signature'].replace('\n', ' ')
        if new_sig != poem['signature']:
            poem['signature'] = new_sig
            changed = True

if changed:
    with open('poems.json', 'w') as f:
        json.dump(poems, f, indent=2)
    print('Signatures cleaned.')
else:
    print('No changes needed.') 