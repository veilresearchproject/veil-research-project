/* SIGNAL research protocol preflight: standalone, read-only, no device control. */
export function validateStudyDraft(study) {
  const issues = [];
  const add = (field, message) => issues.push({ field, message });
  if (!study || typeof study !== 'object' || Array.isArray(study)) {
    return { ready: false, issues: [{ field: 'study', message: 'A study object is required.' }], status: 'DRAFT ONLY — not evidence or approval' };
  }
  const required = [
    'hypothesis', 'null_hypothesis', 'primary_outcome', 'control_condition',
    'analysis_plan', 'blinding_plan', 'consent_plan', 'uncertainty_plan',
    'human_review_plan', 'clock_sync_plan'
  ];
  if (typeof study.protocol_id !== 'string' || !/^[A-Za-z0-9][A-Za-z0-9_-]{2,59}$/.test(study.protocol_id)) {
    add('protocol_id', 'Use 3–60 letters, digits, dashes or underscores.');
  }
  for (const field of required) {
    if (typeof study[field] !== 'string' || !study[field].trim() || study[field].length > 1500) {
      add(field, 'Provide a nonempty plan of at most 1500 characters.');
    }
  }
  const date = (field) => {
    const v = study[field];
    if (typeof v !== 'string' || !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(v)) {
      add(field, 'Use UTC YYYY-MM-DDTHH:MM:SSZ.');
      return null;
    }
    const t = Date.parse(v);
    if (!Number.isFinite(t) || new Date(t).toISOString().slice(0, 19) + 'Z' !== v) {
      add(field, 'Invalid UTC date or time.');
      return null;
    }
    return t;
  };
  const registered = date('preregistered_at_utc');
  const planned = date('planned_start_utc');
  if (registered !== null && planned !== null && registered >= planned) {
    add('preregistered_at_utc', 'Must precede the planned session; retrospectively documented studies are not preregistered.');
  }
  if (!Array.isArray(study.sources) || study.sources.length < 2 || study.sources.length > 12) {
    add('sources', 'List 2–12 independently identified evidence devices.');
  } else {
    const ids = new Set();
    study.sources.forEach((source, i) => {
      if (!source || typeof source !== 'object' || Array.isArray(source)) {
        add(`sources[${i}]`, 'Source must be an object.');
        return;
      }
      for (const field of ['device_id', 'modality', 'clock_reference']) {
        if (typeof source[field] !== 'string' || !source[field].trim() || source[field].length > 120) {
          add(`sources[${i}].${field}`, 'Required nonempty text, at most 120 characters.');
        }
      }
      if (typeof source.device_id === 'string' && source.device_id.trim()) {
        if (ids.has(source.device_id.trim())) add(`sources[${i}].device_id`, 'Duplicate device identifier.');
        ids.add(source.device_id.trim());
      }
    });
  }
  return { ready: issues.length === 0, issues, status: 'DRAFT ONLY — not evidence or approval' };
}
