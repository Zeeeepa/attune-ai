'use client';

import { useState } from 'react';

interface SBARStep {
  stepNumber: number;
  stepName: string;
  title: string;
  description: string;
  prompts: string[];
  fields: FormField[];
}

interface FormField {
  name: string;
  type: 'text' | 'textarea' | 'select';
  label: string;
  placeholder?: string;
  required: boolean;
  options?: string[];
}

interface SBARWizardProps {
  onComplete?: (report: any) => void;
}

export default function SBARWizard({ onComplete }: SBARWizardProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [wizardId, setWizardId] = useState<string | null>(null);
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [finalReport, setFinalReport] = useState<string | null>(null);

  const steps: Record<number, SBARStep> = {
    1: {
      stepNumber: 1,
      stepName: 'Situation',
      title: 'Current Situation',
      description: 'Describe the current patient situation and immediate concerns',
      prompts: [
        'What is the patient\'s current condition?',
        'What brought the patient to your attention?',
        'What are the immediate concerns or changes?',
        'What is the patient\'s current status?',
      ],
      fields: [
        {
          name: 'patient_condition',
          type: 'textarea',
          label: 'Current patient condition',
          placeholder: 'Describe the patient\'s current state...',
          required: true,
        },
        {
          name: 'immediate_concerns',
          type: 'textarea',
          label: 'Immediate concerns',
          placeholder: 'What concerns brought this to your attention?',
          required: true,
        },
        {
          name: 'vital_signs',
          type: 'text',
          label: 'Current vital signs',
          placeholder: 'BP, HR, RR, Temp, O2 Sat',
          required: false,
        },
      ],
    },
    2: {
      stepNumber: 2,
      stepName: 'Background',
      title: 'Clinical Background',
      description: 'Provide relevant clinical background and history',
      prompts: [
        'What is the patient\'s medical history?',
        'What treatments have been provided?',
        'What are the relevant clinical details?',
        'What is the patient\'s baseline condition?',
      ],
      fields: [
        {
          name: 'medical_history',
          type: 'textarea',
          label: 'Relevant medical history',
          placeholder: 'Include pertinent diagnoses, allergies, medications...',
          required: true,
        },
        {
          name: 'current_treatments',
          type: 'textarea',
          label: 'Current treatments/interventions',
          placeholder: 'What has been done so far?',
          required: true,
        },
        {
          name: 'baseline_condition',
          type: 'textarea',
          label: 'Patient\'s baseline condition',
          placeholder: 'How does this compare to the patient\'s normal state?',
          required: false,
        },
      ],
    },
    3: {
      stepNumber: 3,
      stepName: 'Assessment',
      title: 'Clinical Assessment',
      description: 'Your professional assessment of the situation',
      prompts: [
        'What is your clinical assessment?',
        'What do you think is happening?',
        'What are your concerns?',
        'What is your professional judgment?',
      ],
      fields: [
        {
          name: 'clinical_assessment',
          type: 'textarea',
          label: 'Your clinical assessment',
          placeholder: 'Based on your nursing judgment, what do you think is happening?',
          required: true,
        },
        {
          name: 'primary_concerns',
          type: 'textarea',
          label: 'Primary clinical concerns',
          placeholder: 'What are you most worried about?',
          required: true,
        },
        {
          name: 'risk_factors',
          type: 'textarea',
          label: 'Identified risk factors',
          placeholder: 'What factors increase risk or complicate care?',
          required: false,
        },
      ],
    },
    4: {
      stepNumber: 4,
      stepName: 'Recommendation',
      title: 'Recommendations',
      description: 'What actions do you recommend?',
      prompts: [
        'What do you need from the physician?',
        'What actions should be taken?',
        'What is the timeline for action?',
        'What are your specific recommendations?',
      ],
      fields: [
        {
          name: 'recommendations',
          type: 'textarea',
          label: 'Specific recommendations',
          placeholder: 'What specific actions do you recommend?',
          required: true,
        },
        {
          name: 'requested_actions',
          type: 'textarea',
          label: 'Requested physician actions',
          placeholder: 'What do you need the physician to do?',
          required: true,
        },
        {
          name: 'timeline',
          type: 'select',
          label: 'Urgency level',
          required: true,
          options: ['Immediate', 'Within 30 minutes', 'Within 1 hour', 'Within 4 hours', 'Routine'],
        },
      ],
    },
  };

  const startWizard = async () => {
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/api/wizards/sbar/start', {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to start SBAR wizard');
      }

      const data = await response.json();
      setWizardId(data.data?.wizard_session?.wizard_id || data.wizard_id);
      setCurrentStep(1);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start wizard');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFieldChange = (fieldName: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [`step_${currentStep}_${fieldName}`]: value,
    }));
  };

  const validateStep = (): boolean => {
    const step = steps[currentStep];
    const requiredFields = step.fields.filter(f => f.required);

    for (const field of requiredFields) {
      const value = formData[`step_${currentStep}_${field.name}`];
      if (!value || value.trim() === '') {
        setError(`Please fill in: ${field.label}`);
        return false;
      }
    }

    return true;
  };

  const submitStep = async () => {
    if (!validateStep()) {
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const step = steps[currentStep];
      const stepData: Record<string, any> = {};

      step.fields.forEach(field => {
        const value = formData[`step_${currentStep}_${field.name}`];
        if (value) {
          stepData[field.name] = value;
        }
      });

      if (currentStep === 4) {
        // Generate final report
        const response = await fetch('/api/wizards/sbar/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            patient_id: 'PT-' + Date.now(),
            situation: Object.entries(formData)
              .filter(([k]) => k.startsWith('step_1_'))
              .map(([_, v]) => v)
              .join('\n'),
            background: Object.entries(formData)
              .filter(([k]) => k.startsWith('step_2_'))
              .map(([_, v]) => v)
              .join('\n'),
            assessment: Object.entries(formData)
              .filter(([k]) => k.startsWith('step_3_'))
              .map(([_, v]) => v)
              .join('\n'),
            recommendation: Object.entries(formData)
              .filter(([k]) => k.startsWith('step_4_'))
              .map(([_, v]) => v)
              .join('\n'),
            care_setting: 'med-surg',
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to generate SBAR report');
        }

        const data = await response.json();
        setFinalReport(data.sbar_report);

        if (onComplete) {
          onComplete(data);
        }
      } else {
        // Move to next step
        setCurrentStep(currentStep + 1);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit step');
    } finally {
      setIsLoading(false);
    }
  };

  const goBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      setError('');
    }
  };

  const reset = () => {
    setCurrentStep(1);
    setWizardId(null);
    setFormData({});
    setFinalReport(null);
    setError('');
  };

  if (!wizardId) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-[var(--background)] border-2 border-[var(--border)] rounded-lg p-8 text-center">
          <div className="text-6xl mb-6">📋</div>
          <h2 className="text-3xl font-bold mb-4">SBAR Clinical Handoff Wizard</h2>
          <p className="text-lg text-[var(--text-secondary)] mb-8 max-w-2xl mx-auto">
            Guided workflow for creating structured SBAR (Situation, Background, Assessment, Recommendation) handoff reports.
            This wizard will walk you through each component step-by-step.
          </p>

          <div className="grid md:grid-cols-4 gap-4 mb-8">
            {Object.values(steps).map((step) => (
              <div key={step.stepNumber} className="p-4 bg-[var(--border)] bg-opacity-20 rounded-lg">
                <div className="text-2xl font-bold text-[var(--primary)] mb-2">
                  Step {step.stepNumber}
                </div>
                <div className="text-sm font-semibold mb-1">{step.stepName}</div>
                <div className="text-xs text-[var(--text-secondary)]">
                  {step.fields.length} fields
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={startWizard}
            disabled={isLoading}
            className="btn btn-primary text-lg px-12 py-4 disabled:opacity-50"
          >
            {isLoading ? 'Starting...' : 'Start SBAR Wizard'}
          </button>
        </div>
      </div>
    );
  }

  if (finalReport) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-[var(--background)] border-2 border-[var(--success)] rounded-lg p-8">
          <div className="text-center mb-6">
            <div className="text-6xl mb-4">✅</div>
            <h2 className="text-3xl font-bold mb-2">SBAR Report Complete</h2>
            <p className="text-[var(--text-secondary)]">
              Your structured handoff report has been generated
            </p>
          </div>

          <div className="bg-[var(--border)] bg-opacity-10 rounded-lg p-6 mb-6">
            <pre className="whitespace-pre-wrap font-mono text-sm">{finalReport}</pre>
          </div>

          <div className="flex gap-4">
            <button
              onClick={() => navigator.clipboard.writeText(finalReport)}
              className="flex-1 btn btn-secondary"
            >
              📋 Copy to Clipboard
            </button>
            <button onClick={reset} className="flex-1 btn btn-primary">
              🔄 Create Another Report
            </button>
          </div>
        </div>
      </div>
    );
  }

  const step = steps[currentStep];
  const progress = (currentStep / 4) * 100;

  return (
    <div className="max-w-4xl mx-auto">
      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-semibold">
            Step {currentStep} of 4: {step.stepName}
          </span>
          <span className="text-sm text-[var(--text-secondary)]">
            {Math.round(progress)}% Complete
          </span>
        </div>
        <div className="w-full bg-[var(--border)] bg-opacity-30 rounded-full h-3">
          <div
            className="bg-[var(--primary)] h-3 rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <div className="bg-[var(--background)] border-2 border-[var(--border)] rounded-lg p-8">
        {/* Step Header */}
        <div className="mb-8">
          <div className="text-4xl mb-4">
            {currentStep === 1 ? '🩺' : currentStep === 2 ? '📋' : currentStep === 3 ? '🔍' : '💡'}
          </div>
          <h2 className="text-3xl font-bold mb-3">{step.title}</h2>
          <p className="text-lg text-[var(--text-secondary)] mb-4">{step.description}</p>

          {/* Guiding Prompts */}
          <div className="bg-[var(--primary)] bg-opacity-5 border-l-4 border-[var(--primary)] p-4 rounded">
            <p className="text-sm font-semibold mb-2">Consider these questions:</p>
            <ul className="text-sm space-y-1">
              {step.prompts.map((prompt, idx) => (
                <li key={idx} className="text-[var(--text-secondary)]">• {prompt}</li>
              ))}
            </ul>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-[var(--error)] bg-opacity-10 border-2 border-[var(--error)] rounded-lg">
            <p className="text-[var(--error)]">{error}</p>
          </div>
        )}

        {/* Form Fields */}
        <div className="space-y-6 mb-8">
          {step.fields.map((field) => (
            <div key={field.name}>
              <label className="block text-sm font-bold mb-2">
                {field.label}
                {field.required && <span className="text-[var(--error)]"> *</span>}
              </label>

              {field.type === 'textarea' ? (
                <textarea
                  rows={4}
                  value={formData[`step_${currentStep}_${field.name}`] || ''}
                  onChange={(e) => handleFieldChange(field.name, e.target.value)}
                  placeholder={field.placeholder}
                  className="w-full px-4 py-3 rounded-lg border-2 border-[var(--border)] bg-[var(--background)] focus:border-[var(--primary)] focus:outline-none"
                />
              ) : field.type === 'select' ? (
                <select
                  value={formData[`step_${currentStep}_${field.name}`] || ''}
                  onChange={(e) => handleFieldChange(field.name, e.target.value)}
                  className="w-full px-4 py-3 rounded-lg border-2 border-[var(--border)] bg-[var(--background)] focus:border-[var(--primary)] focus:outline-none"
                >
                  <option value="">Select...</option>
                  {field.options?.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  type="text"
                  value={formData[`step_${currentStep}_${field.name}`] || ''}
                  onChange={(e) => handleFieldChange(field.name, e.target.value)}
                  placeholder={field.placeholder}
                  className="w-full px-4 py-3 rounded-lg border-2 border-[var(--border)] bg-[var(--background)] focus:border-[var(--primary)] focus:outline-none"
                />
              )}
            </div>
          ))}
        </div>

        {/* Navigation Buttons */}
        <div className="flex gap-4">
          <button
            onClick={goBack}
            disabled={currentStep === 1 || isLoading}
            className="flex-1 btn btn-outline disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ← Previous
          </button>
          <button
            onClick={submitStep}
            disabled={isLoading}
            className="flex-1 btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-white"></span>
                Processing...
              </span>
            ) : currentStep === 4 ? (
              '✅ Generate Report'
            ) : (
              'Next →'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
