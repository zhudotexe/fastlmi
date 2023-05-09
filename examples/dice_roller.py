import d20  # pip install d20
from pydantic import BaseModel

import fastlmi
from fastlmi import FastLMI

app = FastLMI(
    title="Dice Roller",
    name_for_model="DiceRoller",
    description="A simple plugin to roll dice.",
    description_for_model=(
        "DiceRoller can roll dice in XdY format and do math.\n"
        "Some dice examples are:\n"
        "4d6kh3 :: highest 3 of 4 6-sided dice\n"
        "2d6ro<3 :: roll 2d6s, then reroll any 1s or 2s once\n"
        "8d6mi2 :: roll 8d6s, with each die having a minimum roll of 2\n"
        "(1d4 + 1, 3, 2d6kl1)kh1 :: the highest of 1d4+1, 3, and the lower of 2 d6s\n"
        "Normal math operations are also supported."
    ),
    contact_email="foo@example.com",
    legal_url="https://example.com/legal",
)
# use this when developing localhost plugins to allow the browser to make the local request
fastlmi.utils.cors_allow_openai(app)


class DiceRequest(BaseModel):
    dice: str  # the dice to roll


class DiceResponse(BaseModel):
    result: str  # the resulting dice string
    total: int  # the total numerical result of the roll (rounded down to nearest integer)


@app.post("/roll")
def roll(dice: DiceRequest) -> DiceResponse:
    """Roll the given dice and return a detailed result."""
    result = d20.roll(dice.dice)
    return DiceResponse(result=result.result, total=result.total)
