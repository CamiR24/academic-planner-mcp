TECHNIQUES = {
    "memorización": {
        "technique": "Repetición espaciada + Active Recall",
        "justification": (
            "Para contenido memorístico (fechas, fórmulas, vocabulario, definiciones), "
            "recordar activamente la información en intervalos crecientes de tiempo "
            "fortalece la retención mucho más que releer pasivamente."
        ),
        "how_to": (
            "Crea flashcards con la pregunta de un lado y la respuesta del otro. "
            "Revísalas hoy, luego en 1 día, luego en 3 días, luego en 7 días. "
            "Antes de ver la respuesta, intenta recordarla desde cero."
        ),
    },
    "conceptual": {
        "technique": "Técnica Feynman + Elaboración",
        "justification": (
            "Para contenido que requiere comprensión profunda (teorías, relaciones causa-efecto, "
            "modelos), explicar el concepto con tus propias palabras, como si se lo enseñaras "
            "a alguien sin conocimiento previo, expone rápidamente qué partes no entiendes bien."
        ),
        "how_to": (
            "Elige el concepto, explícalo en voz alta o por escrito en lenguaje simple. "
            "Cuando te trabes o uses palabras técnicas sin explicarlas, regresa al material "
            "para reforzar esa parte específica, y vuelve a intentar la explicación."
        ),
    },
    "práctico": {
        "technique": "Práctica deliberada con ejercicios progresivos",
        "justification": (
            "Para habilidades aplicadas (programar, resolver problemas de matemática, "
            "diseñar circuitos), la comprensión teórica no garantiza que sepas ejecutarla; "
            "se necesita práctica activa con retroalimentación inmediata."
        ),
        "how_to": (
            "Resuelve ejercicios de dificultad creciente sin ver la solución primero. "
            "Revisa el error apenas te equivoques (no acumules errores sin corregir), "
            "y repite variantes del mismo tipo de problema hasta que lo resuelvas con fluidez."
        ),
    },
}


def recommend_study_technique(content_type: str, time_available_hours: float) -> dict:
    entry = TECHNIQUES.get(content_type, TECHNIQUES["conceptual"])

    time_note = (
        "Con poco tiempo disponible, enfócate en una sola sesión concentrada sin distracciones."
        if time_available_hours < 1.5
        else "Con este tiempo disponible, puedes dividir la sesión en bloques de 25-30 min con descansos breves (técnica Pomodoro)."
    )

    return {
        "technique": entry["technique"],
        "justification": entry["justification"],
        "how_to_apply": entry["how_to"],
        "time_management_tip": time_note,
    }