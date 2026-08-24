// Reads the YAML data files at build time. The repo IS the database.
import fs from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';

const DATA = path.resolve(process.cwd(), '../data');

export function loadMachines() {
  const dir = path.join(DATA, 'machines');
  return fs.readdirSync(dir)
    .filter((f) => f.endsWith('.yaml') && !f.startsWith('_'))
    .map((f) => yaml.load(fs.readFileSync(path.join(dir, f), 'utf8')))
    .sort((a, b) => (a.vendor + a.model).localeCompare(b.vendor + b.model));
}

export function loadCoefficients() {
  return yaml.load(fs.readFileSync(path.join(DATA, 'reference/coefficients.yaml'), 'utf8'));
}

export function loadConditions() {
  return yaml.load(fs.readFileSync(path.join(DATA, 'reference/capability_conditions.yaml'), 'utf8'));
}

// --- Capacity normalization. Mirrors scripts/normalize.py exactly. ---
// Validated: Ritz-Carlton 16.5 ac/day x 7 working days / 3.5 mows per week
// = 33.0 managed acres, against 32.7 acres of actual fairway.

export function dailyCapacityAc(m, sessionHours = 5.5) {
  const cap = m.capacity || {};
  const { basis, value } = cap;
  const freq = cap.vendor_assumed_mow_freq;
  if (value == null) return null;
  if (basis === 'ac_per_hr') return value * sessionHours;
  if (basis === 'ac_per_day') return value;
  if (basis === 'ac_per_week') return value / 7;
  if (basis === 'ac_managed_vendor') {
    if (freq == null) return null; // unnormalizable - vendor states no frequency
    return (value * freq) / 7;
  }
  return null;
}

export function managedAcres(m, mowFreqPerWeek, sessionHours = 5.5) {
  const workingDays = m.economic_engine === 'duty_cycle' ? 7 : 5;
  const daily = dailyCapacityAc(m, sessionHours);
  if (daily == null || !mowFreqPerWeek) return null;
  return (daily * workingDays) / mowFreqPerWeek;
}

export function isBlocked(m) {
  const cap = m.capacity || {};
  return cap.basis === 'ac_managed_vendor' && cap.vendor_assumed_mow_freq == null;
}

export const SURFACES = [
  ['greens', 'Greens'],
  ['tees', 'Tees'],
  ['approaches', 'Approaches'],
  ['fairways', 'Fairways'],
  ['intermediate_rough', 'Int. rough'],
  ['primary_rough', 'Rough'],
  ['driving_range', 'Range'],
];

export const CLASS_LABEL = {
  manual: 'Manual',
  semi_autonomous: 'Semi-autonomous',
  fully_autonomous: 'Fully autonomous',
};
