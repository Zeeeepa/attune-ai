"""ECG Waveform Signal Analyzer.

Standalone module for extracting morphological features from raw ECG
waveform data.  Detects R-peaks, measures QRS duration, estimates QT
interval (with Bazett correction), evaluates ST-segment deviation,
checks P-wave presence, and classifies T-wave morphology.

Requires numpy and scipy as optional dependencies.  When they are not
installed the analyzer returns a stub WaveformFeatures with a warning
so that callers degrade gracefully.

Reference sampling rate: 360 Hz (MIT-BIH Arrhythmia Database default).

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional dependency check
# ---------------------------------------------------------------------------

try:
    import numpy as np
    from scipy.signal import butter, filtfilt, find_peaks

    _HAS_NUMPY_SCIPY = True
except ImportError:
    _HAS_NUMPY_SCIPY = False
    np = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Clinical threshold constants
# ---------------------------------------------------------------------------

# QRS duration (ms)
QRS_NORMAL_MIN: float = 80.0
QRS_NORMAL_MAX: float = 120.0
QRS_PROLONGED_THRESHOLD: float = 120.0
QRS_WIDE_THRESHOLD: float = 160.0

# QT interval (ms) — pre-correction reference range
QT_NORMAL_MIN: float = 350.0
QT_NORMAL_MAX: float = 440.0

# ST segment deviation (mV)
ST_ELEVATION_THRESHOLD: float = 0.1
ST_DEPRESSION_THRESHOLD: float = -0.1

# Signal quality tiers
QUALITY_GOOD: float = 0.8
QUALITY_FAIR: float = 0.5

# Bandpass filter design parameters (Hz)
_BANDPASS_LOW: float = 0.5
_BANDPASS_HIGH: float = 40.0
_FILTER_ORDER: int = 4

# P-wave search window relative to R-peak (samples at 360 Hz)
_P_WAVE_EARLY_MS: float = 200.0
_P_WAVE_LATE_MS: float = 120.0

# J-point offset for ST measurement (ms after QRS end)
_J_POINT_OFFSET_MS: float = 60.0


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class WaveformFeatures:
    """Morphological features extracted from an ECG waveform.

    Attributes:
        qrs_duration_ms: Median QRS complex duration in milliseconds.
        qt_interval_ms: QT interval in milliseconds (uncorrected).
        qtc_interval_ms: Bazett-corrected QTc interval in milliseconds.
        st_deviation_mv: Mean ST-segment deviation in millivolts.
            Positive values indicate elevation; negative indicate depression.
        p_wave_present: Whether a P-wave was detected before the majority
            of R-peaks.
        t_wave_morphology: T-wave shape classification.  One of
            ``"normal"``, ``"inverted"``, or ``"flat"``.
        heart_rate_bpm: Estimated heart rate derived from R-R intervals.
        signal_quality: Signal quality score from 0.0 (unusable) to
            1.0 (excellent), estimated from signal-to-noise ratio.
        r_peak_count: Number of R-peaks detected in the signal.
        waveform_summary: Nurse-friendly plain-language summary of the
            extracted features.
    """

    qrs_duration_ms: float = 0.0
    qt_interval_ms: float = 0.0
    qtc_interval_ms: float = 0.0
    st_deviation_mv: float = 0.0
    p_wave_present: bool = False
    t_wave_morphology: str = "normal"
    heart_rate_bpm: float = 0.0
    signal_quality: float = 0.0
    r_peak_count: int = 0
    waveform_summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize features to a plain dictionary.

        Returns:
            JSON-serializable dictionary of all feature fields.
        """
        return {
            "qrs_duration_ms": self.qrs_duration_ms,
            "qt_interval_ms": self.qt_interval_ms,
            "qtc_interval_ms": self.qtc_interval_ms,
            "st_deviation_mv": self.st_deviation_mv,
            "p_wave_present": self.p_wave_present,
            "t_wave_morphology": self.t_wave_morphology,
            "heart_rate_bpm": self.heart_rate_bpm,
            "signal_quality": self.signal_quality,
            "r_peak_count": self.r_peak_count,
            "waveform_summary": self.waveform_summary,
        }


# ---------------------------------------------------------------------------
# Analyzer
# ---------------------------------------------------------------------------


class ECGWaveformAnalyzer:
    """Analyze raw ECG waveform signals to extract morphological features.

    The analyzer works standalone and does not depend on the CDS agent
    system.  It accepts a 1-D NumPy array of voltage samples and returns
    a :class:`WaveformFeatures` dataclass.

    Args:
        sampling_rate: Samples per second.  Defaults to 360 Hz
            (MIT-BIH Arrhythmia Database standard).

    Example:
        >>> import numpy as np
        >>> analyzer = ECGWaveformAnalyzer(sampling_rate=360)
        >>> signal = np.random.randn(3600)  # 10 seconds at 360 Hz
        >>> features = analyzer.analyze_signal(signal)
        >>> print(features.waveform_summary)
    """

    def __init__(self, sampling_rate: int = 360) -> None:
        if sampling_rate <= 0:
            raise ValueError("sampling_rate must be a positive integer")
        self.sampling_rate: int = sampling_rate

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze_signal(
        self,
        signal: Any,
        annotations: list[Any] | None = None,
    ) -> WaveformFeatures:
        """Extract morphological features from a raw ECG signal.

        Args:
            signal: 1-D NumPy array of ECG voltage samples.
            annotations: Optional list of beat annotations (unused in
                the current implementation but reserved for future
                annotation-guided analysis).

        Returns:
            :class:`WaveformFeatures` populated with measured values and
            a nurse-friendly summary string.

        Raises:
            RuntimeError: If numpy/scipy are not installed.
        """
        if not _HAS_NUMPY_SCIPY:
            logger.warning(
                "numpy and scipy are required for ECG waveform analysis. "
                "Install them with: pip install numpy scipy"
            )
            return WaveformFeatures(
                waveform_summary="Waveform analysis unavailable (numpy/scipy not installed).",
            )

        signal = np.asarray(signal, dtype=np.float64).ravel()

        if signal.size < self.sampling_rate:
            logger.warning(
                "Signal too short for reliable analysis (%d samples, "
                "need at least %d).",
                signal.size,
                self.sampling_rate,
            )
            return WaveformFeatures(
                waveform_summary="Signal too short for analysis.",
            )

        # Step 1 — Bandpass filter and quality estimation
        filtered = self._bandpass_filter(signal)
        quality = self._estimate_signal_quality(signal, filtered)

        # Step 2 — R-peak detection
        r_peaks = self._detect_r_peaks(filtered)

        if len(r_peaks) < 2:
            logger.info("Fewer than 2 R-peaks detected; limited analysis.")
            return WaveformFeatures(
                signal_quality=quality,
                r_peak_count=len(r_peaks),
                waveform_summary="Insufficient R-peaks for full analysis.",
            )

        # Step 3 — Derived measurements
        rr_intervals = np.diff(r_peaks) / self.sampling_rate  # seconds
        mean_rr = float(np.mean(rr_intervals))
        heart_rate = 60.0 / mean_rr if mean_rr > 0 else 0.0

        qrs_ms = self._measure_qrs_duration(filtered, r_peaks)
        qt_ms = self._estimate_qt_interval(mean_rr)
        qtc_ms = self._bazett_correction(qt_ms, mean_rr)
        st_dev = self._measure_st_deviation(filtered, r_peaks)
        p_present = self._detect_p_wave(filtered, r_peaks)
        t_morph = self._classify_t_wave(filtered, r_peaks, mean_rr)

        features = WaveformFeatures(
            qrs_duration_ms=round(qrs_ms, 1),
            qt_interval_ms=round(qt_ms, 1),
            qtc_interval_ms=round(qtc_ms, 1),
            st_deviation_mv=round(st_dev, 3),
            p_wave_present=p_present,
            t_wave_morphology=t_morph,
            heart_rate_bpm=round(heart_rate, 1),
            signal_quality=round(quality, 2),
            r_peak_count=len(r_peaks),
        )
        features.waveform_summary = self.format_for_nurse(features)
        return features

    def format_for_nurse(self, features: WaveformFeatures) -> str:
        """Produce a plain-language summary suitable for bedside nursing staff.

        Args:
            features: Previously computed :class:`WaveformFeatures`.

        Returns:
            Human-readable string summarizing the ECG findings.
        """
        parts: list[str] = []

        # Rhythm regularity (simplified)
        if features.heart_rate_bpm > 0:
            parts.append(f"Heart rate {features.heart_rate_bpm:.0f} bpm.")
        else:
            parts.append("Heart rate could not be determined.")

        # QRS
        if features.qrs_duration_ms > 0:
            if features.qrs_duration_ms <= QRS_NORMAL_MAX:
                parts.append(f"QRS normal width ({features.qrs_duration_ms:.0f}ms).")
            elif features.qrs_duration_ms <= QRS_WIDE_THRESHOLD:
                parts.append(
                    f"QRS prolonged ({features.qrs_duration_ms:.0f}ms, "
                    f"normal <{QRS_NORMAL_MAX:.0f}ms)."
                )
            else:
                parts.append(
                    f"QRS wide ({features.qrs_duration_ms:.0f}ms, "
                    f"normal <{QRS_NORMAL_MAX:.0f}ms)."
                )

        # ST segment
        if features.st_deviation_mv > ST_ELEVATION_THRESHOLD:
            parts.append(
                f"ST elevation noted ({features.st_deviation_mv:+.2f}mV)."
            )
        elif features.st_deviation_mv < ST_DEPRESSION_THRESHOLD:
            parts.append(
                f"ST depression noted ({features.st_deviation_mv:+.2f}mV)."
            )
        else:
            parts.append("No significant ST changes.")

        # QT / QTc
        if features.qtc_interval_ms > 0:
            qtc_status = "normal range" if features.qtc_interval_ms <= QT_NORMAL_MAX else "prolonged"
            parts.append(
                f"QTc interval {features.qtc_interval_ms:.0f}ms ({qtc_status})."
            )

        # P-wave
        if features.p_wave_present:
            parts.append("P-waves present.")
        else:
            parts.append("P-waves not clearly identified.")

        # T-wave
        if features.t_wave_morphology == "inverted":
            parts.append("T-wave inversion noted.")
        elif features.t_wave_morphology == "flat":
            parts.append("T-waves appear flattened.")

        # Signal quality
        if features.signal_quality >= QUALITY_GOOD:
            quality_label = "good"
        elif features.signal_quality >= QUALITY_FAIR:
            quality_label = "fair"
        else:
            quality_label = "poor"
        parts.append(f"Signal quality: {quality_label}.")

        return " ".join(parts)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _bandpass_filter(self, signal: Any) -> Any:
        """Apply a Butterworth bandpass filter to the raw signal.

        Args:
            signal: 1-D numpy array of raw ECG samples.

        Returns:
            Filtered signal array.
        """
        nyquist = self.sampling_rate / 2.0
        low = _BANDPASS_LOW / nyquist
        high = min(_BANDPASS_HIGH / nyquist, 0.99)

        b, a = butter(_FILTER_ORDER, [low, high], btype="band")
        return filtfilt(b, a, signal)

    def _estimate_signal_quality(self, raw: Any, filtered: Any) -> float:
        """Estimate signal quality as a 0-1 score based on SNR.

        Uses the ratio of filtered-signal RMS to noise RMS, where noise
        is defined as ``raw - filtered``.

        Args:
            raw: Original unfiltered signal.
            filtered: Bandpass-filtered signal.

        Returns:
            Quality score between 0.0 and 1.0.
        """
        noise = raw - filtered
        signal_rms = float(np.sqrt(np.mean(filtered**2)))
        noise_rms = float(np.sqrt(np.mean(noise**2)))

        if noise_rms == 0:
            return 1.0

        snr = signal_rms / noise_rms
        # Map SNR to 0-1 using a sigmoid-like curve (SNR ~3 -> ~0.9)
        quality = 1.0 - 1.0 / (1.0 + snr)
        return max(0.0, min(1.0, quality))

    def _detect_r_peaks(self, filtered: Any) -> Any:
        """Detect R-peaks in a filtered ECG signal.

        Uses :func:`scipy.signal.find_peaks` with adaptive height and
        distance constraints based on the sampling rate.

        Args:
            filtered: Bandpass-filtered ECG signal.

        Returns:
            NumPy array of R-peak sample indices.
        """
        # Minimum distance between R-peaks: ~200ms (300 bpm ceiling)
        min_distance = int(0.2 * self.sampling_rate)

        # Adaptive height: at least 0.5 * std of signal
        height_threshold = 0.5 * float(np.std(filtered))

        peaks, _ = find_peaks(
            filtered,
            height=height_threshold,
            distance=min_distance,
        )
        return peaks

    def _measure_qrs_duration(self, filtered: Any, r_peaks: Any) -> float:
        """Measure median QRS duration by analysing gradient changes.

        For each R-peak, the method searches backward and forward from
        the peak for the point where the absolute gradient drops below a
        threshold, marking the QRS onset and offset respectively.

        Args:
            filtered: Bandpass-filtered ECG signal.
            r_peaks: Array of R-peak sample indices.

        Returns:
            Median QRS duration in milliseconds.
        """
        gradient = np.abs(np.gradient(filtered))
        grad_threshold = 0.15 * float(np.max(gradient))
        # Max search radius: 100ms on each side
        max_radius = int(0.1 * self.sampling_rate)

        durations: list[float] = []
        for peak in r_peaks:
            # Search backward for QRS onset
            onset = peak
            for i in range(1, max_radius + 1):
                idx = peak - i
                if idx < 0:
                    break
                if gradient[idx] < grad_threshold:
                    onset = idx
                    break

            # Search forward for QRS offset
            offset = peak
            for i in range(1, max_radius + 1):
                idx = peak + i
                if idx >= len(filtered):
                    break
                if gradient[idx] < grad_threshold:
                    offset = idx
                    break

            duration_samples = offset - onset
            if duration_samples > 0:
                duration_ms = (duration_samples / self.sampling_rate) * 1000.0
                durations.append(duration_ms)

        if not durations:
            return 0.0

        return float(np.median(durations))

    def _estimate_qt_interval(self, mean_rr_sec: float) -> float:
        """Estimate QT interval from the mean R-R interval.

        Uses the empirical relationship QT ~ 0.4 * RR (at normal heart
        rates) as a first-order approximation when beat-level T-wave end
        detection is not available.

        Args:
            mean_rr_sec: Mean R-R interval in seconds.

        Returns:
            Estimated QT interval in milliseconds.
        """
        if mean_rr_sec <= 0:
            return 0.0
        # QT ~ 0.4 * RR (in seconds), converted to ms
        return 0.4 * mean_rr_sec * 1000.0

    @staticmethod
    def _bazett_correction(qt_ms: float, rr_sec: float) -> float:
        """Apply Bazett correction to a QT interval.

        QTc = QT / sqrt(RR), where QT is in milliseconds and RR in
        seconds.

        Args:
            qt_ms: Uncorrected QT interval in milliseconds.
            rr_sec: R-R interval in seconds.

        Returns:
            Corrected QTc in milliseconds.
        """
        if rr_sec <= 0 or qt_ms <= 0:
            return 0.0
        return qt_ms / math.sqrt(rr_sec)

    def _measure_st_deviation(self, filtered: Any, r_peaks: Any) -> float:
        """Measure mean ST-segment deviation relative to the PR baseline.

        Samples the signal at the J-point + 60 ms after each R-peak and
        compares to the PR-segment baseline (120 ms before the R-peak).

        Args:
            filtered: Bandpass-filtered ECG signal.
            r_peaks: Array of R-peak sample indices.

        Returns:
            Mean ST deviation in millivolts (positive = elevation).
        """
        j_offset_samples = int((_J_POINT_OFFSET_MS / 1000.0) * self.sampling_rate)
        # QRS half-width estimate: ~50ms
        qrs_half = int(0.05 * self.sampling_rate)
        # ST measurement point: QRS offset + J-point offset
        st_offset = qrs_half + j_offset_samples

        # PR baseline: 120ms before R-peak
        pr_offset = int(0.12 * self.sampling_rate)

        deviations: list[float] = []
        for peak in r_peaks:
            st_idx = peak + st_offset
            pr_idx = peak - pr_offset

            if pr_idx < 0 or st_idx >= len(filtered):
                continue

            baseline = float(filtered[pr_idx])
            st_level = float(filtered[st_idx])
            deviations.append(st_level - baseline)

        if not deviations:
            return 0.0

        return float(np.mean(deviations))

    def _detect_p_wave(self, filtered: Any, r_peaks: Any) -> bool:
        """Detect P-wave presence by searching for a small positive deflection.

        Searches 120-200 ms before each R-peak for a local maximum that
        exceeds a low amplitude threshold.  P-waves are considered present
        if found before at least 60 % of R-peaks.

        Args:
            filtered: Bandpass-filtered ECG signal.
            r_peaks: Array of R-peak sample indices.

        Returns:
            True if P-waves are present in the majority of beats.
        """
        early_samples = int((_P_WAVE_EARLY_MS / 1000.0) * self.sampling_rate)
        late_samples = int((_P_WAVE_LATE_MS / 1000.0) * self.sampling_rate)

        # Amplitude threshold: small fraction of R-peak amplitude
        median_r_amp = float(np.median(np.abs(filtered[r_peaks])))
        p_threshold = 0.05 * median_r_amp

        found_count = 0
        checked_count = 0

        for peak in r_peaks:
            start = peak - early_samples
            end = peak - late_samples
            if start < 0 or end < 0 or start >= end:
                continue
            checked_count += 1

            segment = filtered[start:end]
            if len(segment) == 0:
                continue

            local_max = float(np.max(segment))
            if local_max > p_threshold:
                found_count += 1

        if checked_count == 0:
            return False

        return (found_count / checked_count) >= 0.6

    def _classify_t_wave(
        self,
        filtered: Any,
        r_peaks: Any,
        mean_rr_sec: float,
    ) -> str:
        """Classify T-wave morphology at the expected T-wave location.

        Samples the signal at approximately 60 % of the R-R interval
        after each R-peak and evaluates the median amplitude relative
        to the R-peak amplitude.

        Args:
            filtered: Bandpass-filtered ECG signal.
            r_peaks: Array of R-peak sample indices.
            mean_rr_sec: Mean R-R interval in seconds.

        Returns:
            One of ``"normal"``, ``"inverted"``, or ``"flat"``.
        """
        if mean_rr_sec <= 0:
            return "normal"

        # T-wave expected at ~60% of RR after R-peak
        t_offset = int(0.6 * mean_rr_sec * self.sampling_rate)

        median_r_amp = float(np.median(np.abs(filtered[r_peaks])))
        flat_threshold = 0.03 * median_r_amp

        amplitudes: list[float] = []
        for peak in r_peaks:
            t_idx = peak + t_offset
            if t_idx >= len(filtered):
                continue
            amplitudes.append(float(filtered[t_idx]))

        if not amplitudes:
            return "normal"

        median_t = float(np.median(amplitudes))

        if abs(median_t) < flat_threshold:
            return "flat"
        if median_t < 0:
            return "inverted"
        return "normal"
