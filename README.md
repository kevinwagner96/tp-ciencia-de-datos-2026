# Trabajo Práctico Integrador - Ciencia de Datos

**Cursado Intensivo 2026**

Una popular plataforma de venta de videojuegos quiere construir un sistema recomendador para ofrecer a sus usuarios nuevas opciones con base en sus preferencias personales.

El cliente no posee valores explícitos sobre las preferencias de los usuarios, por lo que estas deberán ser inferidas a partir de otras variables.

## Dataset

El cliente manifiesta que posee una base de datos con las siguientes columnas:

| Columna | Tipo | Descripción |
| :--- | :--- | :--- |
| **ID del usuario** | Integer | Identificador único del usuario. |
| **Título del juego** | String | Nombre único del juego. |
| **Comportamiento** | String | Tipo de comportamiento que tuvo el usuario (comprar o jugar el juego). |
| **Horas** | Float | En caso de que el comportamiento sea “jugar”, indica la cantidad de horas jugadas.<br>En caso de que el comportamiento sea “comprar”, el valor es 1.0. |
| **Value** | Int | 0, sin datos. |

## Consignas

1. **Motor de Recomendación**: Desarrollar un motor de recomendación utilizando el lenguaje de programación de su preferencia. Este motor debe funcionar de manera independiente a cualquier otro sistema que lo consuma.
2. **API REST**: El sistema deberá proveer una API REST para poder ser consultado. La misma deberá recibir como entrada el identificador del usuario y un número `k`, y deberá devolver las `k` recomendaciones para este usuario.
3. **Cold Start**: El sistema deberá permitir realizar recomendaciones para cualquier nuevo usuario, sin interacciones previas. Considere que no se incorporarán nuevos títulos a la lista de videojuegos.
4. **Entregables**: Presentar un repositorio en GitHub. No se requerirá la documentación en CRISP-DM, pero sí cierta documentación para poder justificar las decisiones que se toman, utilizando al menos un Jupyter Notebook para el entendimiento de los datos (EDA) y para la validación del sistema.
