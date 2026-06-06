export type ProfileRole = 'paramedic' | 'hospital';
export type UserRole = ProfileRole | null;
export type TransferStatus =
  | 'waiting'
  | 'approved'
  | 'rejected'
  | 'transferring'
  | 'completed'
  | 'cancelled';

export interface PatientData {
  consciousness: string;
  respiration: string;
  bloodPressure: string;
  pulse: string;
  oxygenSaturation: string;
  temperature: string;
  symptoms: string;
  existingHospital?: string; // Added field
  ktasLevel: number | null;
}

export interface Hospital {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  availableBeds: number;
  eta?: number;
  distance?: number;
  specialties: string[];
  acceptanceRate?: number;
  phoneNumber?: string;
  reasonSummary?: string;
  coverageLevel?: 'FULL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'NONE';
  coverageScore?: number;
  mkioskFlags?: string[];
  address?: string;
}

export interface TransferRequest {
  id: string;
  patientData: PatientData;
  hospitalId: string;
  hospitalName: string;
  status: TransferStatus;
  timestamp: Date;
  paramedicName: string;
  paramedicUnit: string;
}

export interface HospitalRequest {
  id: string;
  ktasLevel: number;
  consciousness: string;
  symptoms: string;
  eta: number;
  paramedicUnit: string;
  paramedicName: string;
  timestamp: Date;
  status: TransferStatus;
  patientData: PatientData;
}
