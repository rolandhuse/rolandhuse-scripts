# MenuTitle: Build Roman Numerals with Features
__doc__ = """
Builds Roman numeral glyphs and adds OpenType substitutions for stylistic sets and ligatures.
Adds to existing ss01/liga features without overwriting them, and ensures ss01 precedes liga.
"""

import traceback
from GlyphsApp import *
from GlyphsApp.plugins import *

def create_roman_glyphs(font):
    roman_glyphs = [
        ("2160", "Ⅰ", ["I"]),
        ("2161", "Ⅱ", ["I", "I"]),
        ("2162", "Ⅲ", ["I", "I", "I"]),
        ("2163", "Ⅳ", ["I", "V"]),
        ("2164", "Ⅴ", ["V"]),
        ("2165", "Ⅵ", ["V", "I"]),
        ("2166", "Ⅶ", ["V", "I", "I"]),
        ("2167", "Ⅷ", ["V", "I", "I", "I"]),
        ("2168", "Ⅸ", ["I", "X"]),
        ("2169", "Ⅹ", ["X"]),
        ("216A", "Ⅺ", ["X", "I"]),
        ("216B", "Ⅻ", ["X", "I", "I"]),
        ("216C", "Ⅼ", ["L"]),
        ("216D", "Ⅽ", ["C"]),
        ("216E", "Ⅾ", ["D"]),
        ("216F", "Ⅿ", ["M"]),
        ("", "Twenty-roman", ["X", "X"]),
    ]

    for unicode_hex, glyph_name, components in roman_glyphs:
        try:
            if font.glyphs[glyph_name]:
                print(f"⚠️ Skipping {glyph_name}: Exists.")
                continue

            new_glyph = GSGlyph()
            new_glyph.name = glyph_name
            if unicode_hex:
                new_glyph.unicode = unicode_hex
                new_glyph.productionName = f"uni{unicode_hex}"
            font.glyphs.append(new_glyph)
            print(f"✅ Created {glyph_name}")

            for master in font.masters:
                master_id = master.id
                new_layer = GSLayer()
                new_layer.associatedMasterId = master_id
                x_position = 0

                for component_name in components:
                    component_glyph = font.glyphs[component_name]
                    if not component_glyph:
                        print(f"   ⚠️ Missing component: {component_name}")
                        continue

                    component = GSComponent(component_name)
                    component.automaticAlignment = True
                    component.position = (x_position, 0)
                    new_layer.components.append(component)

                    component_layer = component_glyph.layers[master_id]
                    x_position += component_layer.width

                new_layer.width = x_position
                new_glyph.layers[master_id] = new_layer

        except Exception as e:
            print(f"❌ Error in {glyph_name}: {e}")
            traceback.print_exc()

def add_opentype_features(font):
    ss01_rules = """
  # Single substitutions (Arabic to Roman)
  sub one by One-roman;
  sub two by Two-roman;
  sub three by Three-roman;
  sub four by Four-roman;
  sub five by Five-roman;
  sub six by Six-roman;
  sub seven by Seven-roman;
  sub eight by Eight-roman;
  sub nine by Nine-roman;
"""

    liga_rules = """
  # Ligature substitutions
  sub one zero by Ten-roman;
  sub one one by Eleven-roman;
  sub one two by Twelve-roman;
  sub two zero by Twenty-roman;
  sub five zero by Fifty-roman;
  sub one zero zero by Hundred-roman;
  sub five zero zero by Fivehundred-roman;
  sub one zero zero zero by Thousand-roman;
"""

    def update_feature(feature_name, rules):
        feature = font.features[feature_name]
        if feature:
            if rules.strip() not in feature.code:
                if feature.code.strip().endswith("}"):
                    new_code = feature.code.strip()[:-1].rstrip() + f"\n{rules}\n}}"
                else:
                    new_code = feature.code + f"\n{rules}"
                feature.code = new_code
                print(f"✅ Added to existing {feature_name} feature")
            else:
                print(f"⚠️ Rules already exist in {feature_name}")
        else:
            new_feature = GSFeature()
            new_feature.name = feature_name
            new_feature.code = f"feature {feature_name} {{\n{rules}\n}}"
            font.features.append(new_feature)
            print(f"✅ Created new {feature_name} feature")

    # Add and update features
    update_feature("ss01", ss01_rules)
    update_feature("liga", liga_rules)

    # Ensure ss01 precedes liga
    feature_names = [f.name for f in font.features]
    if "ss01" in feature_names and "liga" in feature_names:
        if feature_names.index("liga") < feature_names.index("ss01"):
            ss01 = font.features["ss01"]
            liga = font.features["liga"]
            font.features.remove(ss01)
            font.features.remove(liga)
            font.features.append(ss01)
            font.features.append(liga)
            print("✅ Reordered: ss01 now precedes liga")

# Run
if __name__ == "__main__":
    font = Glyphs.font
    if font:
        create_roman_glyphs(font)
        add_opentype_features(font)

        Message(
            title="Roman Numerals with OT Features Added!",
            message="Type 2025 with Roman numerals: 10001000205\n\n(Please enable both ss01 and standard ligatures OpenType Features)",
            OKButton="Got it!"
        )

        font.newTab("2025 = 10001000205")

        print("🎉 Done! Features updated and ordered.")
    else:
        print("⚠️ No font open.")