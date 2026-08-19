from scipy import constants as const


class ConversionService:
    JOULE_UNITS = {"j", "ev", "k", "hz", "rad_s", "t"}
    SUPPORTED_UNITS = JOULE_UNITS | {"nm"}

    @classmethod
    def convert(cls, value: float, source_unit: str, target_unit: str) -> float:
        if source_unit == target_unit:
            return value

        if source_unit not in cls.SUPPORTED_UNITS or target_unit not in cls.SUPPORTED_UNITS:
            supported = ", ".join(sorted(cls.SUPPORTED_UNITS))
            raise ValueError(f"Unsupported unit. Supported units are: {supported}.")

        joules = cls._to_joules(value, source_unit)
        return cls._from_joules(joules, target_unit)

    @classmethod
    def _to_joules(cls, value: float, source_unit: str) -> float:
        if source_unit == "j":
            return value
        if source_unit == "ev":
            return value * const.e
        if source_unit == "k":
            return value * const.Boltzmann
        if source_unit == "hz":
            return const.h * value
        if source_unit == "rad_s":
            return const.hbar * value
        if source_unit == "t":
            return const.physical_constants["Bohr magneton"][0] * value
        if source_unit == "nm":
            if value <= 0:
                raise ValueError("Wavelength must be greater than 0.")
            return (const.h * const.c) / (value * 1e-9)
        raise ValueError(f"Unsupported source unit '{source_unit}'.")

    @classmethod
    def _from_joules(cls, joules: float, target_unit: str) -> float:
        if target_unit == "j":
            return joules
        if target_unit == "ev":
            return joules / const.e
        if target_unit == "k":
            return joules / const.Boltzmann
        if target_unit == "hz":
            return joules / const.h
        if target_unit == "rad_s":
            return joules / const.hbar
        if target_unit == "t":
            return joules / const.physical_constants["Bohr magneton"][0]
        if target_unit == "nm":
            if joules <= 0:
                raise ValueError(
                    "Cannot convert non-positive energy to wavelength in nm."
                )
            return (const.h * const.c / joules) * 1e9
        raise ValueError(f"Unsupported target unit '{target_unit}'.")
