def filter_perfumes(perfumes, gender, budget, season, mood, note):
    results = []
    for p in perfumes:
        match = True
        
        if gender and gender not in p['gender']:
            match = False
        if budget and budget not in p['budget']:
            match = False
        if season and season not in p['season']:
            match = False
        if mood and mood not in p['mood']:
            match = False
        if note and note not in p['notes']:
            match = False
            
        if match:
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