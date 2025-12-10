import React, { useState, useEffect } from 'react';
import { 
  Bell, 
  Settings, 
  LogOut, 
  Bed, 
  Activity, 
  Filter, 
  Clock, 
  CheckCircle2, 
  XCircle,
  AlertTriangle,
  User,
  Heart,
  Wind,
  Brain,
  Thermometer,
  ChevronDown,
  Loader2
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  ModernButton, 
  ModernCard, 
  TEXT_TITLE, 
  cn 
} from './ui/DesignSystem';
import { HospitalRequest } from '../types';
import { supabase } from '../utils/supabase/client';

interface HospitalDashboardProps {
  onLogout: () => void;
}

export const HospitalDashboard: React.FC<HospitalDashboardProps> = ({ onLogout }) => {
  const [requests, setRequests] = useState<HospitalRequest[]>([]);
  const [rejectModalOpen, setRejectModalOpen] = useState<string | null>(null); // Request ID
  const [hospitalId] = useState<string>('1'); // Hardcoded for prototype (Seoul Nat'l Univ Hospital) - In real app, get from user profile
  const [bedStatus, setBedStatus] = useState({ available: 0, total: 20 });
  const [isLoading, setIsLoading] = useState(false);

  // Fetch Initial Data
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      
      // 1. Fetch Requests (Assume hospital_id matches the one in DB. Since we used UUIDs in the guide, we might need to query by name or just fetch all for demo if ID is unknown)
      // For this prototype, to make it work immediately after "seed data", we need the ID of '서울대학교병원'.
      // So let's first fetch the hospital ID by name '서울대학교병원' to be safe.
      
      let targetHospitalId = hospitalId;
      
      const { data: hospData } = await supabase
        .from('hospitals')
        .select('id')
        .eq('name', '서울대학교병원')
        .single();
        
      if (hospData) {
        targetHospitalId = hospData.id;
        // Update local state if needed, but for now we just use it for queries
      }

      // 2. Fetch Requests
      const { data: reqData, error: reqError } = await supabase
        .from('transfer_requests')
        .select('*')
        .eq('hospital_id', targetHospitalId)
        .eq('status', 'waiting')
        .order('created_at', { ascending: false });

      if (reqData) {
        const mappedRequests: HospitalRequest[] = reqData.map((r: any) => ({
          id: r.id,
          ktasLevel: r.ktas_level,
          consciousness: 'Alert', // Default or map if available
          symptoms: r.symptoms,
          eta: 10, // Mock or calculate
          paramedicUnit: '119 구급대',
          paramedicName: '대원',
          timestamp: new Date(r.created_at),
          status: r.status,
          patientData: {
            consciousness: r.consciousness || 'Alert',
            respiration: r.vitals_resp?.toString() || '-',
            bloodPressure: r.vitals_bp || '-',
            pulse: r.vitals_pulse?.toString() || '-',
            temperature: r.vitals_temp?.toString() || '36.5',
            symptoms: r.symptoms,
            ktasLevel: r.ktas_level
          }
        }));
        setRequests(mappedRequests);
      }

      // 3. Fetch Hospital Status
      const { data: statusData } = await supabase
        .from('hospital_status')
        .select('available_beds, total_beds')
        .eq('hospital_id', targetHospitalId)
        .single();
      
      if (statusData) {
        setBedStatus({
            available: statusData.available_beds,
            total: statusData.total_beds || 20
        });
      }

      setIsLoading(false);
      
      // 4. Real-time Subscription
      const channel = supabase
        .channel('hospital-dashboard')
        .on(
            'postgres_changes',
            {
                event: 'INSERT',
                schema: 'public',
                table: 'transfer_requests',
                filter: `hospital_id=eq.${targetHospitalId}`
            },
            (payload) => {
                const r = payload.new;
                const newReq: HospitalRequest = {
                    id: r.id,
                    ktasLevel: r.ktas_level,
                    consciousness: r.consciousness || 'Alert',
                    symptoms: r.symptoms,
                    eta: 15, // Mock
                    paramedicUnit: '119 구급대',
                    paramedicName: '신규 요청',
                    timestamp: new Date(r.created_at),
                    status: r.status,
                    patientData: {
                        consciousness: r.consciousness || 'Alert',
                        respiration: r.vitals_resp?.toString() || '-',
                        bloodPressure: r.vitals_bp || '-',
                        pulse: r.vitals_pulse?.toString() || '-',
                        temperature: r.vitals_temp?.toString() || '-',
                        symptoms: r.symptoms,
                        ktasLevel: r.ktas_level
                    }
                };
                setRequests(prev => [newReq, ...prev]);
            }
        )
        .subscribe();

      return () => {
          supabase.removeChannel(channel);
      };
    };

    fetchData();
  }, [hospitalId]);

  const handleApprove = async (id: string) => {
    setRequests(prev => prev.filter(req => req.id !== id));
    
    const { error } = await supabase
        .from('transfer_requests')
        .update({ status: 'approved' })
        .eq('id', id);

    if (error) {
        alert("오류가 발생했습니다.");
    } else {
        // Decrement local bed count optimistically
        setBedStatus(prev => ({ ...prev, available: Math.max(0, prev.available - 1) }));
        
        // Update DB bed count (Naive approach for prototype)
        // Ideally should be an RPC or trigger
        const { data: hospData } = await supabase.from('hospitals').select('id').eq('name', '서울대학교병원').single();
        if (hospData) {
            const { data: currentStatus } = await supabase.from('hospital_status').select('available_beds').eq('hospital_id', hospData.id).single();
            if (currentStatus) {
                await supabase.from('hospital_status').update({ available_beds: Math.max(0, currentStatus.available_beds - 1) }).eq('hospital_id', hospData.id);
            }
        }
    }
  };

  const handleReject = async (id: string, reason: string) => {
    setRequests(prev => prev.filter(req => req.id !== id));
    setRejectModalOpen(null);

    await supabase
        .from('transfer_requests')
        .update({ status: 'rejected', rejection_reason: reason })
        .eq('id', id);
  };

  return (
    <div className="flex flex-col min-h-screen bg-[#F5F7FA] font-sans text-slate-800 max-w-md mx-auto relative shadow-2xl overflow-hidden">
      
      {/* Header */}
      <header className="bg-white border-b border-gray-100 p-4 flex items-center justify-between sticky top-0 z-20">
        <div>
           <h1 className="text-xl font-bold text-gray-900 leading-none">응급실 대시보드</h1>
           <p className="text-sm text-gray-500 font-medium">서울대학교병원 ER</p>
        </div>
        <div className="flex items-center gap-3">
           <button className="p-2 relative rounded-full hover:bg-gray-100">
              <Bell size={24} className="text-gray-600" />
              {requests.length > 0 && (
                <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
              )}
           </button>
           <button onClick={onLogout} className="p-2 rounded-full hover:bg-gray-100">
              <LogOut size={24} className="text-gray-600" />
           </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-4 pb-20">
        
        {/* Status Summary Cards */}
        <section className="grid grid-cols-2 gap-3 mb-6">
            <ModernCard className="p-4 bg-white border-l-4 border-l-[#388E3C] !shadow-sm">
                <div className="flex justify-between items-start mb-2">
                    <span className="text-xs font-bold text-gray-500 uppercase">가용 병상 (ER)</span>
                    <Bed size={16} className="text-[#388E3C]" />
                </div>
                <div className="flex items-baseline gap-1">
                    <span className="text-3xl font-black text-[#388E3C]">{bedStatus.available}</span>
                    <span className="text-sm text-gray-400 font-medium">/ {bedStatus.total}</span>
                </div>
            </ModernCard>

            <ModernCard className="p-4 bg-white border-l-4 border-l-orange-500 !shadow-sm">
                 <div className="flex justify-between items-start mb-2">
                    <span className="text-xs font-bold text-gray-500 uppercase">중환자실 (ICU)</span>
                    <Activity size={16} className="text-orange-500" />
                </div>
                <div className="flex items-baseline gap-1">
                    <span className="text-3xl font-black text-orange-500">1</span>
                    <span className="text-sm text-gray-400 font-medium">/ 8</span>
                </div>
            </ModernCard>
        </section>

        {/* Filter Bar */}
        <div className="flex justify-between items-center mb-4 px-1">
            <h2 className="text-lg font-bold text-gray-800 flex items-center gap-2">
                실시간 이송 요청 <span className="bg-red-100 text-[#C0392B] text-xs px-2 py-0.5 rounded-full">{requests.length}</span>
            </h2>
            <button className="flex items-center gap-1 text-sm font-bold text-gray-500 bg-white border border-gray-200 px-3 py-1.5 rounded-lg shadow-sm">
                <Filter size={14} />
                전체 등급
                <ChevronDown size={14} />
            </button>
        </div>

        {/* Requests List */}
        <div className="space-y-4">
            {isLoading ? (
                <div className="flex justify-center py-10">
                    <Loader2 className="animate-spin text-gray-400" />
                </div>
            ) : (
            <AnimatePresence>
                {requests.map((req) => (
                    <motion.div 
                        key={req.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, height: 0, marginBottom: 0 }}
                        layout
                    >
                        <ModernCard className={cn(
                            "relative overflow-hidden border-2",
                            req.ktasLevel === 1 ? "border-red-100 bg-red-50/30" : "border-gray-100"
                        )}>
                            {/* Header: KTAS & Time */}
                            <div className="flex items-center justify-between mb-4">
                                <div className={cn(
                                    "flex items-center gap-2 px-3 py-1.5 rounded-lg font-black",
                                    req.ktasLevel === 1 ? "bg-red-600 text-white" : 
                                    req.ktasLevel === 2 ? "bg-orange-500 text-white" :
                                    "bg-yellow-400 text-black"
                                )}>
                                    <span className="text-xs uppercase tracking-wider">KTAS</span>
                                    <span className="text-xl leading-none">{req.ktasLevel}</span>
                                </div>
                                <div className="flex items-center gap-1.5 text-[#00796B] font-bold bg-[#E0F2F1] px-3 py-1.5 rounded-lg">
                                    <Clock size={16} />
                                    <span>{req.eta}분 후 도착</span>
                                </div>
                            </div>

                            {/* Patient Info */}
                            <div className="mb-5 space-y-2">
                                <div className="flex items-start gap-3">
                                    <div className="mt-1 min-w-[20px]">
                                        <AlertTriangle size={20} className="text-gray-400" />
                                    </div>
                                    <p className="font-bold text-gray-900 text-lg leading-snug">
                                        {req.symptoms}
                                    </p>
                                </div>
                                
                                <div className="flex items-center gap-4 text-sm text-gray-600 pl-[32px]">
                                    <span className="flex items-center gap-1 bg-white px-2 py-1 rounded border border-gray-200">
                                        <Brain size={14} className="text-gray-400" />
                                        {req.consciousness}
                                    </span>
                                    <span className="flex items-center gap-1 bg-white px-2 py-1 rounded border border-gray-200">
                                        <Heart size={14} className="text-gray-400" />
                                        {req.patientData.pulse}
                                    </span>
                                    <span className="flex items-center gap-1 bg-white px-2 py-1 rounded border border-gray-200">
                                        <Wind size={14} className="text-gray-400" />
                                        {req.patientData.respiration}
                                    </span>
                                </div>
                                <p className="text-xs text-gray-400 font-medium pl-[32px] pt-1">
                                    {req.paramedicUnit} • {req.paramedicName}
                                </p>
                            </div>

                            {/* Action Buttons */}
                            <div className="grid grid-cols-2 gap-3">
                                <ModernButton 
                                    onClick={() => setRejectModalOpen(req.id)}
                                    className="bg-white text-gray-600 border-2 border-gray-200 hover:bg-gray-50 hover:text-red-600 hover:border-red-200 shadow-none font-bold"
                                >
                                    <XCircle size={20} />
                                    거절 (NO)
                                </ModernButton>
                                <ModernButton 
                                    onClick={() => handleApprove(req.id)}
                                    variant="success"
                                    className="font-bold shadow-lg shadow-green-100"
                                >
                                    <CheckCircle2 size={20} />
                                    승인 (YES)
                                </ModernButton>
                            </div>
                        </ModernCard>
                    </motion.div>
                ))}
            </AnimatePresence>
            )}

            {!isLoading && requests.length === 0 && (
                <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex flex-col items-center justify-center py-12 text-center text-gray-400"
                >
                    <div className="p-4 bg-gray-100 rounded-full mb-4">
                        <CheckCircle2 size={48} className="text-gray-300" />
                    </div>
                    <p className="text-lg font-bold">대기 중인 요청이 없습니다</p>
                    <p className="text-sm">새로운 이송 요청이 오면 알림이 울립니다</p>
                </motion.div>
            )}
        </div>
      </main>

      {/* Rejection Modal Overlay */}
      <AnimatePresence>
        {rejectModalOpen && (
            <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-end sm:items-center justify-center"
                onClick={() => setRejectModalOpen(null)}
            >
                <motion.div 
                    initial={{ y: "100%" }}
                    animate={{ y: 0 }}
                    exit={{ y: "100%" }}
                    transition={{ type: "spring", damping: 25, stiffness: 300 }}
                    className="bg-white w-full max-w-md rounded-t-3xl sm:rounded-3xl p-6 shadow-2xl"
                    onClick={(e) => e.stopPropagation()}
                >
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-xl font-bold text-gray-900">거절 사유 선택</h3>
                        <button onClick={() => setRejectModalOpen(null)} className="p-2 hover:bg-gray-100 rounded-full">
                            <XCircle size={24} className="text-gray-400" />
                        </button>
                    </div>

                    <div className="grid grid-cols-1 gap-3 mb-6">
                        {['병상 부족 (ER Full)', '전문 의료진 부재', '수술실/장비 부족', 'ICU 병상 부족', '기타 사유'].map((reason) => (
                            <button
                                key={reason}
                                onClick={() => handleReject(rejectModalOpen, reason)}
                                className="w-full text-left p-4 rounded-xl border-2 border-gray-100 hover:border-red-200 hover:bg-red-50 hover:text-red-700 font-bold text-gray-600 transition-all flex justify-between items-center group"
                            >
                                {reason}
                                <ChevronDown className="opacity-0 group-hover:opacity-100 -rotate-90 text-red-400" size={20} />
                            </button>
                        ))}
                    </div>
                </motion.div>
            </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
