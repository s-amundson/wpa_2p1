

class Choices:
    def bows(self):
        return [('', 'None'),
                ('barebow', 'Barebow/Basic Compound'),
                ('recurve', 'Recurve/Para Recurve Open'),
                ('compound', 'Compound/Para Compound Open/W1/Fixed Pins**')]

    def distances(self):
        return [(None, None), (9, 9), (18, 18)]

    def event_types(self):
        return [('joad_indoor', 'JOAD Indoor'), ('other', 'Other')]

    def pin_shoot_catagory(self):
        return [('joad_indoor', 'JOAD Indoor')]

    def stars(self):
        return [(0, "0, None"),
                (1, "1, Green"),
                (2, "2, Purple"),
                (3, "3, Grey"),
                (4, "4, White"),
                (5, "5, Black"),
                (6, "6, Blue"),
                (7, "7, Red"),
                (8, "8, Yellow"),
                (9, "9, Bronze"),
                (10, "10, Silver"),
                (11, "11, Gold")
                ]

    def targets(self):
        return [(None, None), (40, 40), (60, 60), (80, 80), (122, 122)]
