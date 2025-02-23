


def _transform_date(date_str: str) -> str:
    
	month_map = {
        'enero': '01',
		'febrero': '02',
		'marzo': '03',
		'abril': '04',
		'mayo': '05',
		'junio': '06',
		'julio': '07',
		'agosto': '08',
		'septiembre': '09',
		'octubre': '10',
		'noviembre': '11',
		'diciembre': '12'
	}
    
	day, month, year = date_str.split(' de ')
	month_num = month_map[month.lower()]
	return f"{day}-{month_num}-{year}"