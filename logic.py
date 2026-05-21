def filter_perfumes(perfumes, gender, budget, season, mood):
    results = []
    for p in perfumes:
        if (p['gender'] == gender and
            p['budget'] == budget and
            p['season'] == season and
            p['mood'] == mood):
            results.append(p)
    return results

def get_longevity_label(hours):
    if hours <= 4:
        return 'Short lasting'
    elif hours <= 7:
        return 'Moderate'
    elif hours <= 10:
        return 'Long lasting'
    else:
        return 'Very long lasting'

def is_already_in_favorites(favorites, perfume_id):
    for fav in favorites:
        if fav['perfume_id'] == perfume_id:
            return True
    return False

def get_budget_display(budget):
    labels = {
        'budget': 'Budget-Friendly',
        'mid': 'Mid-Range',
        'luxury': 'Luxury'
    }
    return labels.get(budget, budget)