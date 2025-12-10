import React, { useState } from 'react';
import { Ambulance, Hospital, ArrowRight } from 'lucide-react';
import { ChunkyButton, ChunkyInput, TEXT_TITLE } from './ui/DesignSystem';
import { UserRole } from '../types';

interface LoginPageProps {
  onLogin: (role: UserRole, name: string) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
  const [step, setStep] = useState<'role' | 'auth'>('role');
  const [selectedRole, setSelectedRole] = useState<UserRole>(null);
  const [name, setName] = useState('');
  const [affiliation, setAffiliation] = useState('');

  const handleRoleSelect = (role: UserRole) => {
    setSelectedRole(role);
    setStep('auth');
  };

  const handleSubmit = () => {
    if (selectedRole && name && affiliation) {
      // We are passing name + affiliation as a combined string or just name for now based on App.tsx signature
      // App.tsx expects (role, name). We'll pass the name.
      onLogin(selectedRole, `${name} (${affiliation})`);
    }
  };

  if (step === 'role') {
    return (
      <div className="flex-1 flex flex-col p-6 gap-6 justify-center bg-slate-900 min-h-screen">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-black text-white leading-none mb-2 tracking-tighter">EMS<br/>CONNECT</h1>
          <p className="text-xl font-bold text-slate-400">응급 환자 이송 시스템</p>
        </div>
        
        <div className="flex-1 flex flex-col gap-6 max-h-[600px]">
          <button 
            onClick={() => handleRoleSelect('paramedic')}
            className="flex-1 bg-red-600 active:bg-red-700 rounded-3xl border-b-[12px] border-red-800 active:border-b-0 active:translate-y-3 transition-all flex flex-col items-center justify-center gap-4 group"
          >
            <Ambulance size={80} className="text-white group-hover:scale-110 transition-transform" />
            <span className="text-4xl font-black text-white tracking-wider">구급대원</span>
          </button>

          <button 
            onClick={() => handleRoleSelect('hospital')}
            className="flex-1 bg-blue-600 active:bg-blue-700 rounded-3xl border-b-[12px] border-blue-800 active:border-b-0 active:translate-y-3 transition-all flex flex-col items-center justify-center gap-4 group"
          >
            <Hospital size={80} className="text-white group-hover:scale-110 transition-transform" />
            <span className="text-4xl font-black text-white tracking-wider">병원 의료진</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col p-6 gap-8 bg-white min-h-screen">
      <div className="mt-8">
        <button 
          onClick={() => setStep('role')}
          className="text-lg font-bold text-gray-500 mb-4 flex items-center gap-2"
        >
          ← 뒤로가기
        </button>
        <h2 className="text-4xl font-black text-gray-900 mb-2">로그인</h2>
        <p className="text-xl text-gray-600 font-bold">
          {selectedRole === 'paramedic' ? '구급대원 정보를 입력하세요' : '병원 관계자 정보를 입력하세요'}
        </p>
      </div>

      <div className="flex flex-col gap-6">
        <div>
          <label className="text-xl font-black text-gray-700 mb-2 block">이름</label>
          <ChunkyInput 
            placeholder="홍길동" 
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>
        <div>
          <label className="text-xl font-black text-gray-700 mb-2 block">소속</label>
          <ChunkyInput 
            placeholder={selectedRole === 'paramedic' ? '강남소방서' : '서울대학교병원'} 
            value={affiliation}
            onChange={(e) => setAffiliation(e.target.value)}
          />
        </div>
      </div>

      <div className="mt-auto">
        <ChunkyButton 
          onClick={handleSubmit} 
          disabled={!name || !affiliation} 
          size="lg"
          className={selectedRole === 'paramedic' ? 'bg-red-600 border-red-800' : 'bg-blue-600 border-blue-800'}
        >
          시작하기 <ArrowRight size={32} />
        </ChunkyButton>
      </div>
    </div>
  );
};
