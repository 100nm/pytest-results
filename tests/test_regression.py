from pydantic import BaseModel

from pytest_results import Regression


class TestRegression:
    def test_check_with_success(self) -> dict[str, str]:
        return {"title": "Hello, World!"}

    async def test_check_with_async(self) -> dict[str, str]:
        return {"title": "Hello, World!"}

    def test_check_with_multiple_check(self, regression: Regression) -> None:
        for i in range(3):
            result = {"title": i}
            regression.check(result)

    def test_check_with_pydantic_base_model(self) -> BaseModel:
        class Model(BaseModel):
            title: str

        return Model(title="Hello, World!")
