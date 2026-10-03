"""Registry — adding a new source must not change the aggregation logic."""

from .protocol import AccessibilityProvider


class ProviderRegistry:
    def __init__(self, providers: list[AccessibilityProvider] | None = None) -> None:
        self._by_name: dict[str, AccessibilityProvider] = {}
        for provider in providers or []:
            self.register(provider)

    def register(self, provider: AccessibilityProvider) -> None:
        if provider.name in self._by_name:
            raise ValueError(f'Provider "{provider.name}" is already registered')
        self._by_name[provider.name] = provider

    def get(self, name: str) -> AccessibilityProvider | None:
        return self._by_name.get(name)

    def get_providers(self) -> list[AccessibilityProvider]:
        return list(self._by_name.values())

    async def aclose(self) -> None:
        for provider in self._by_name.values():
            await provider.aclose()
