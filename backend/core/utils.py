def preparation_file(file, ext, ingredients):
    with open(file + ext, 'w', encoding='utf-8') as f:
        f.write('Shopping_cart:' + '\n')
        f.write('\n')
        counter = 1
        for ingredient in ingredients:
            text = (f'{counter}.'
                    f"{ingredient['ingredient__name'].capitalize()} "
                    f"({ingredient['ingredient__measurement_unit']})"
                    f" - {ingredient['amount']} \n")
            f.write(text)
            counter += 1
