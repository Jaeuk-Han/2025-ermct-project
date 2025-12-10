import React, { useState, useEffect, useCallback } from 'react';
import { 
  ArrowLeft,
  Mic,
  Phone,
  CheckCircle2,
  Activity,
  Heart,
  Thermometer,
  Wind,
  Brain,
  Building,
  Loader2,
  Send,
  Stethoscope,
  ChevronRight,
  Navigation,
  RotateCcw,
  Siren,
  Clock,
  Trophy,
  Medal,
  X
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  ModernButton, 
  ModernCard, 
  ModernInput, 
  ModernSelect,
  TEXT_TITLE, 
  cn 
} from './ui/DesignSystem';
import { Hospital, PatientData } from '../types';
import { supabase } from '../utils/supabase/client';
import {
  routeFromKTAS,
  routeNearest,
  RoutingCandidateResponse,
  RoutingCandidateHospital,
  predictAudio,
} from '../utils/api';
import { useRef } from 'react';

interface ParamedicDashboardProps {
  userName: string;
  onLogout: () => void;
}

type ViewState = 'input' | 'list' | 'confirm' | 'transferring' | 'completed';

export const ParamedicDashboard: React.FC<ParamedicDashboardProps> = ({ userName, onLogout }) => {
  const [view, setView] = useState<ViewState>('input');
  
  // Separate states for Listening vs Processing
  const [isListening, setIsListening] = useState(false);
  const [isProcessingVoice, setIsProcessingVoice] = useState(false);
  
  const [patientData, setPatientData] = useState<PatientData>({
    consciousness: 'Alert',
    respiration: '',
    bloodPressure: '',
    pulse: '',
    temperature: '',
    symptoms: '',
    existingHospital: '',
    ktasLevel: null
  });

  const [hospitals, setHospitals] = useState<Hospital[]>([]);
  const [isLoadingHospitals, setIsLoadingHospitals] = useState(false);
  const [selectedHospital, setSelectedHospital] = useState<Hospital | null>(null);
  const [requestStatus, setRequestStatus] = useState<'waiting' | 'approved' | 'rejected'>('waiting');
  const [currentRequestId, setCurrentRequestId] = useState<string | null>(null);
  const [routingResponse, setRoutingResponse] = useState<RoutingCandidateResponse | null>(null);
  const [userLocation, setUserLocation] = useState<{ lat: number; lon: number } | null>(null);
  const [locationRequested, setLocationRequested] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const mediaChunksRef = useRef<Blob[]>([]);
  const recordTimeoutRef = useRef<number | null>(null);

  // KTAS Logic
  useEffect(() => {
    let level: number | null = null;
    const symptom = patientData.symptoms?.toLowerCase() || '';
    
    if (symptom.includes('가슴') || symptom.includes('통증') || symptom.includes('호흡') || symptom.includes('chest')) {
      level = 1;
    } 
    else if (parseInt(patientData.respiration || '0') > 30 || (parseInt(patientData.respiration || '0') < 10 && patientData.respiration !== '')) {
        level = 1;
    }
    else if (patientData.consciousness !== 'Alert') {
        level = 2;
    }
    else if (symptom.length > 5) {
      level = 3;
    }

    setPatientData(prev => ({ ...prev, ktasLevel: level }));
  }, [patientData.symptoms, patientData.respiration, patientData.consciousness]);

  // Map backend hospital to UI model
  const mapToHospital = useCallback((h: RoutingCandidateHospital): Hospital => ({
    id: h.id,
    name: h.name,
    availableBeds: h.total_effective_beds ?? 0,
    eta: h.duration_sec ? Math.max(1, Math.round(h.duration_sec / 60)) : undefined,
    distance: typeof h.distance === 'number' ? Number((h.distance / 1000).toFixed(1)) : undefined,
    specialties: h.groups_with_beds_labels?.length ? h.groups_with_beds_labels : ['ER'],
    acceptanceRate: h.coverage_score ? Math.round(h.coverage_score * 100) : undefined,
    phoneNumber: h.phone || h.emergency_phone || '',
    reasonSummary: h.reason_summary,
    coverageLevel: h.coverage_level,
    coverageScore: h.coverage_score,
    mkioskFlags: h.mkiosk_flags,
    address: h.address,
  }), []);

  // Fetch backend recommendations once list view opens
  const fetchBackendHospitals = useCallback(async () => {
    if (!patientData.ktasLevel || !patientData.symptoms.trim()) {
      setHospitals([]);
      setRoutingResponse(null);
      return;
    }

    setIsLoadingHospitals(true);
    try {
      const base = await routeFromKTAS({
        ktas_level: patientData.ktasLevel,
        chief_complaint: patientData.symptoms,
        hospital_followup: patientData.existingHospital || undefined,
      });

      setRoutingResponse(base);
      setHospitals(base.hospitals.slice(0, 3).map(mapToHospital));
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      setHospitals([]);
      setRoutingResponse(null);
    } finally {
      setIsLoadingHospitals(false);
    }
  }, [mapToHospital, patientData.existingHospital, patientData.ktasLevel, patientData.symptoms]);

  // Try to refine with geolocation once we already have base routing
  useEffect(() => {
    const refineWithLocation = async () => {
      if (!userLocation || !routingResponse) return;

      const alreadyHasDistance = routingResponse.hospitals.some(
        (h) => typeof h.distance === 'number',
      );
      if (alreadyHasDistance) return;

      setIsLoadingHospitals(true);
      try {
        const nearest = await routeNearest({
          ...routingResponse,
          user_lat: userLocation.lat,
          user_lon: userLocation.lon,
        });
        setRoutingResponse(nearest);
        setHospitals(nearest.hospitals.slice(0, 3).map(mapToHospital));
      } catch (err) {
        console.error('Error fetching nearest recommendations:', err);
      } finally {
        setIsLoadingHospitals(false);
      }
    };

    refineWithLocation();
  }, [mapToHospital, routingResponse, userLocation]);

  // Kick off base fetch when entering list view
  useEffect(() => {
    if (view === 'list' && (!routingResponse || routingResponse.hospitals.length === 0)) {
      fetchBackendHospitals();
    }
  }, [fetchBackendHospitals, view]);

  // Sync hospitals when routingResponse is already available (e.g., from voice)
  useEffect(() => {
    if (routingResponse?.hospitals?.length) {
      setHospitals(routingResponse.hospitals.slice(0, 3).map(mapToHospital));
    }
  }, [routingResponse, mapToHospital]);

  // Request geolocation when entering list view (best-effort)
  useEffect(() => {
    if (view !== 'list' || locationRequested) return;
    if (!('geolocation' in navigator)) return;
    setLocationRequested(true);

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setUserLocation({ lat: pos.coords.latitude, lon: pos.coords.longitude });
      },
      (err) => {
        console.warn('Geolocation error', err);
        // 위치가 안 잡혀도 앱이 멈추지 않도록 그대로 진행
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 },
    );
  }, [locationRequested, view]);

// Real-time Subscription for Transfer Request
  useEffect(() => {
    if (!currentRequestId) return;

    const channel = supabase
      .channel('request-updates')
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'transfer_requests',
          filter: `id=eq.${currentRequestId}`
        },
        (payload) => {
          console.log('Update received:', payload);
          if (payload.new.status === 'approved') {
            setRequestStatus('approved');
          } else if (payload.new.status === 'rejected') {
            setRequestStatus('rejected');
          }
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [currentRequestId]);

  const stopVoiceRecording = () => {
    const recorder = mediaRecorderRef.current;
    if (recordTimeoutRef.current) {
      clearTimeout(recordTimeoutRef.current);
      recordTimeoutRef.current = null;
    }
    if (recorder && recorder.state === "recording") {
      recorder.stop();
    } else {
      setIsListening(false);
    }
  };

  const handleVoiceInput = async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      alert("이 브라우저에서는 음성 녹음이 지원되지 않습니다.");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaChunksRef.current = [];
      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          mediaChunksRef.current.push(e.data);
        }
      };

      recorder.onstop = async () => {
        setIsListening(false);
        const blob = new Blob(mediaChunksRef.current, { type: "audio/webm" });
        stream.getTracks().forEach((t) => t.stop());

        setIsProcessingVoice(true);
        try {
          const formData = new FormData();
          formData.append("audio", blob, "recording.webm");

          const result = await predictAudio(formData);
          setRoutingResponse(result);
          setPatientData((prev) => ({
            ...prev,
            ktasLevel: result.case?.ktas ?? prev.ktasLevel,
            symptoms: result.case?.complaint_label ?? prev.symptoms,
          }));
          setHospitals(result.hospitals.slice(0, 3).map(mapToHospital));
          setView("list");
        } catch (err) {
          console.error("음성 전송 실패:", err);
          alert("음성 인식에 실패했습니다. 다시 시도해 주세요.");
        } finally {
          setIsProcessingVoice(false);
        }
        recordTimeoutRef.current = null;
      };

      recorder.start();
      setIsListening(true);

      recordTimeoutRef.current = window.setTimeout(() => {
        if (recorder.state === "recording") {
          recorder.stop();
        }
      }, 60000);
    } catch (err) {
      console.error("마이크 접근 실패:", err);
      alert("마이크 권한을 허용해 주세요.");
    }
  };

  const handleHospitalSelect = async (hospital: Hospital) => {
    setSelectedHospital(hospital);
    setView('confirm');
    setRequestStatus('waiting');

    // 1. Get current user ID
    const { data: { user } } = await supabase.auth.getUser();
    
    // 2. Create Transfer Request in DB
    const { data, error } = await supabase
        .from('transfer_requests')
        .insert({
            hospital_id: hospital.id,
            paramedic_id: user?.id, 
            patient_age: 45, // Mock
            patient_gender: 'Male', // Mock
            symptoms: patientData.symptoms,
            ktas_level: patientData.ktasLevel,
            vitals_bp: patientData.bloodPressure,
            vitals_resp: parseInt(patientData.respiration || '0'),
            vitals_pulse: parseInt(patientData.pulse || '0'),
            status: 'waiting'
        })
        .select()
        .single();

    if (error) {
        console.error("Supabase insert error:", error);
        // Fallback simulation for demo if DB isn't set up
        setTimeout(() => {
            setRequestStatus('approved');
        }, 2500);
    } else if (data) {
        setCurrentRequestId(data.id);
    }
  };

  const handleStartTransfer = async () => {
    setView('transferring');
    
    if (currentRequestId) {
        await supabase
            .from('transfer_requests')
            .update({ status: 'transferring' })
            .eq('id', currentRequestId);
    }
    
    setTimeout(async () => {
        if (currentRequestId) {
            await supabase
                .from('transfer_requests')
                .update({ status: 'completed' })
                .eq('id', currentRequestId);
        }
        setView('completed');
    }, 5000); 
  };

  const handleBack = () => {
    if (view === 'confirm') setView('list');
    else if (view === 'list') setView('input');
    else if (view === 'input') onLogout();
  };

  const handleReset = () => {
    setView('input');
    setPatientData({
      consciousness: 'Alert',
      respiration: '',
      bloodPressure: '',
      pulse: '',
      temperature: '',
      symptoms: '',
      existingHospital: '',
      ktasLevel: null
    });
    setSelectedHospital(null);
    setRequestStatus('waiting');
    setCurrentRequestId(null);
  };

  return (
    <div className="flex flex-col min-h-screen bg-[#F5F7FA] max-w-md mx-auto relative shadow-2xl overflow-hidden font-sans text-slate-800">
      
      {/* Header */}
      <header className="bg-white border-b border-gray-100 p-4 sticky top-0 z-20 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button onClick={handleBack} className="p-2 -ml-2 rounded-full hover:bg-gray-100 text-gray-600">
            <ArrowLeft size={24} />
          </button>
          <div>
            <h1 className="text-sm font-bold text-gray-400 uppercase tracking-wide">Emergency Transfer</h1>
            <p className="text-lg font-bold text-gray-900 leading-none">{userName}</p>
          </div>
        </div>
        <div className="h-10 w-10 bg-red-50 rounded-full flex items-center justify-center">
            <Stethoscope size={20} className="text-[#C0392B]" />
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative overflow-hidden">
        <AnimatePresence mode="wait">
          
          {/* VIEW: INPUT */}
          {view === 'input' && (
            <motion.div 
              key="input" 
              className="flex-1 overflow-y-auto p-5 pb-24 relative"
              initial={{ x: 20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} exit={{ x: -20, opacity: 0 }}
            >
              {/* 1. LISTENING POPUP */}
              <AnimatePresence>
                {isListening && (
                   <motion.div 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="absolute inset-0 z-50 bg-black/80 backdrop-blur-sm flex flex-col items-center justify-center p-8 text-center rounded-xl"
                   >
                     <motion.div 
                       animate={{ scale: [1, 1.2, 1] }}
                       transition={{ duration: 1.5, repeat: Infinity }}
                       className="bg-red-600 p-6 rounded-full mb-6 shadow-2xl shadow-red-900/50"
                     >
                        <Mic size={48} className="text-white" />
                     </motion.div>
                      <h3 className="text-3xl font-black text-white mb-2">녹음 중...</h3>
                      <p className="text-white/60 text-xl font-bold">멈추려면 아래 버튼을 눌러 주세요</p>
                     
                     <div className="mt-8 flex gap-1 h-8 items-center justify-center">
                        {[1,2,3,4,5].map(i => (
                            <motion.div 
                                key={i}
                                animate={{ height: [10, 32, 10] }}
                                transition={{ duration: 0.5, repeat: Infinity, delay: i * 0.1 }}
                                className="w-2 bg-white rounded-full"
                            />
                        ))}
                     </div>
                      <div className="mt-6">
                        <ModernButton variant="primary" size="lg" onClick={stopVoiceRecording} className="px-6">
                          녹음 중지
                        </ModernButton>
                      </div>
                   </motion.div>
                )}
              </AnimatePresence>

              {/* 2. PROCESSING POPUP */}
              <AnimatePresence>
                {isProcessingVoice && (
                   <motion.div 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="absolute inset-0 z-50 bg-white/95 backdrop-blur-sm flex flex-col items-center justify-center p-8 text-center rounded-xl"
                   >
                     <div className="relative mb-8">
                        <div className="absolute inset-0 bg-teal-100 rounded-full blur-xl opacity-50 animate-pulse"></div>
                        <motion.div 
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                          className="relative bg-white p-4 rounded-full shadow-lg border-4 border-gray-100"
                        >
                           <Loader2 size={48} className="text-[#00796B]" />
                        </motion.div>
                     </div>
                     <h3 className="text-3xl font-black text-gray-900 mb-2">데이터 분석 중</h3>
                     <p className="text-[#00796B] text-lg font-bold animate-pulse">KTAS 등급 산정 및 바이탈 입력...</p>
                   </motion.div>
                )}
              </AnimatePresence>

              {/* NEW: KTAS Live Status Display */}
              <div className="mb-6">
                 <div className={cn(
                    "rounded-2xl p-6 border-4 flex items-center justify-between transition-all duration-300 shadow-lg relative overflow-hidden",
                     patientData.ktasLevel === 1 ? "bg-red-50 border-red-600 shadow-red-100" :
                     patientData.ktasLevel === 2 ? "bg-orange-50 border-orange-500 shadow-orange-100" :
                     patientData.ktasLevel === 3 ? "bg-yellow-50 border-yellow-500 shadow-yellow-100" :
                     patientData.ktasLevel ? "bg-green-50 border-green-500 shadow-green-100" :
                     "bg-white border-gray-200"
                 )}>
                    {patientData.ktasLevel && (
                        <div className={cn(
                            "absolute top-0 right-0 w-32 h-32 transform translate-x-8 -translate-y-8 rounded-full opacity-20",
                            patientData.ktasLevel === 1 ? "bg-red-600" :
                            patientData.ktasLevel === 2 ? "bg-orange-500" :
                            patientData.ktasLevel === 3 ? "bg-yellow-500" :
                            "bg-green-500"
                        )} />
                    )}
                    
                    <div>
                       <h3 className="text-gray-500 font-bold text-sm uppercase tracking-widest mb-2 flex items-center gap-2">
                           <Activity size={16} /> KTAS 자동 분류
                       </h3>
                       <p className={cn(
                          "text-4xl font-black tracking-tight",
                          patientData.ktasLevel === 1 ? "text-red-600" :
                          patientData.ktasLevel === 2 ? "text-orange-600" :
                          patientData.ktasLevel === 3 ? "text-yellow-600" :
                          patientData.ktasLevel ? "text-green-600" :
                          "text-gray-400"
                       )}>
                          {patientData.ktasLevel ? `Level ${patientData.ktasLevel}` : "판정 대기"}
                       </p>
                       <p className="text-sm font-bold text-gray-400 mt-1">
                           {patientData.ktasLevel === 1 ? "즉각적인 처치가 필요한 위급 상황" : 
                            patientData.ktasLevel === 2 ? "생명에 위협이 될 수 있는 긴급 상황" :
                            patientData.ktasLevel === 3 ? "잠재적 응급 상황" :
                            "정보를 입력하면 자동 계산됩니다"}
                       </p>
                    </div>
                    
                    <div className={cn(
                       "h-20 w-20 rounded-2xl flex items-center justify-center font-black text-5xl text-white shadow-md z-10 transition-transform duration-300",
                       patientData.ktasLevel ? "scale-100" : "scale-95 grayscale opacity-30",
                       patientData.ktasLevel === 1 ? "bg-red-600" :
                       patientData.ktasLevel === 2 ? "bg-orange-500" :
                       patientData.ktasLevel === 3 ? "bg-yellow-500" :
                       patientData.ktasLevel ? "bg-green-500" :
                       "bg-gray-200"
                    )}>
                       {patientData.ktasLevel || '-'}
                    </div>
                 </div>
              </div>

              {/* Voice Input Button + Stop */}
              <div className="mb-6 flex flex-col gap-3">
                 <ModernButton 
                    variant="voice" 
                    size="full" 
                    onClick={handleVoiceInput}
                    disabled={isListening || isProcessingVoice}
                    className="flex items-center justify-center gap-3 shadow-lg shadow-indigo-200 py-6"
                 >
                    <Mic size={28} />
                    <span className="font-black text-xl">음성으로 입력하기</span>
                 </ModernButton>
                 <ModernButton
                    variant="secondary"
                    size="full"
                    onClick={stopVoiceRecording}
                    disabled={!isListening}
                    className="flex items-center justify-center gap-2"
                 >
                    <span className="font-bold">{isListening ? '녹음 중지' : '녹음 대기 중'}</span>
                 </ModernButton>
              </div>

              <div className="space-y-6">
                {/* Vitals Section */}
                <section>
                    <h3 className="text-lg font-black text-gray-800 uppercase tracking-tight mb-3 ml-1 flex items-center gap-2">
                        <Activity className="text-red-500" size={20} /> Vitals & Consciousness
                    </h3>
                    <ModernCard className="space-y-6">
                        <div className="grid grid-cols-2 gap-5">
                            <div className="col-span-2">
                                <label className="flex items-center gap-2 text-lg font-bold text-gray-600 mb-2">
                                    <Brain size={20} className="text-[#00796B]" /> 의식상태 (AVPU)
                                </label>
                                <ModernSelect 
                                    value={patientData.consciousness}
                                    onChange={(e) => setPatientData(prev => ({...prev, consciousness: e.target.value}))}
                                    className="!text-2xl !font-black !py-4 !h-16 text-gray-900"
                                >
                                    <option value="Alert">Alert (명료)</option>
                                    <option value="Voice">Voice (언어반응)</option>
                                    <option value="Pain">Pain (통증반응)</option>
                                    <option value="Unresponsive">Unresponsive (무반응)</option>
                                </ModernSelect>
                            </div>
                            
                            <div>
                                <label className="flex items-center gap-2 text-lg font-bold text-gray-600 mb-2">
                                    <Activity size={20} className="text-[#00796B]" /> 혈압
                                </label>
                                <ModernInput 
                                    placeholder="120/80" 
                                    value={patientData.bloodPressure}
                                    onChange={(e) => setPatientData(prev => ({...prev, bloodPressure: e.target.value}))}
                                    className="text-center font-mono !text-2xl !font-black !h-16 tracking-wider"
                                />
                            </div>
                            <div>
                                <label className="flex items-center gap-2 text-lg font-bold text-gray-600 mb-2">
                                    <Heart size={20} className="text-[#00796B]" /> 맥박
                                </label>
                                <ModernInput 
                                    placeholder="80" 
                                    value={patientData.pulse}
                                    onChange={(e) => setPatientData(prev => ({...prev, pulse: e.target.value}))}
                                    type="number"
                                    className="text-center font-mono !text-2xl !font-black !h-16"
                                />
                            </div>
                            <div>
                                <label className="flex items-center gap-2 text-lg font-bold text-gray-600 mb-2">
                                    <Wind size={20} className="text-[#00796B]" /> 호흡
                                </label>
                                <ModernInput 
                                    placeholder="16" 
                                    value={patientData.respiration}
                                    onChange={(e) => setPatientData(prev => ({...prev, respiration: e.target.value}))}
                                    type="number"
                                    className="text-center font-mono !text-2xl !font-black !h-16"
                                />
                            </div>
                            <div>
                                <label className="flex items-center gap-2 text-lg font-bold text-gray-600 mb-2">
                                    <Thermometer size={20} className="text-[#00796B]" /> 체온
                                </label>
                                <ModernInput 
                                    placeholder="36.5" 
                                    value={patientData.temperature}
                                    onChange={(e) => setPatientData(prev => ({...prev, temperature: e.target.value}))}
                                    type="number"
                                    className="text-center font-mono !text-2xl !font-black !h-16"
                                />
                            </div>
                        </div>
                    </ModernCard>
                </section>

                {/* Symptoms & History */}
                <section>
                    <h3 className="text-lg font-black text-gray-800 uppercase tracking-tight mb-3 ml-1 flex items-center gap-2">
                        <Stethoscope className="text-blue-500" size={20} /> Medical Info
                    </h3>
                    <ModernCard className="space-y-6">
                        <div>
                            <label className="text-lg font-bold text-gray-600 mb-2 block">Symptoms</label>
                            <textarea 
                                className="w-full bg-gray-50 border border-gray-200 rounded-2xl p-5 text-2xl font-bold focus:bg-white focus:border-[#00796B] focus:ring-4 focus:ring-[#00796B]/20 outline-none transition-all resize-none leading-snug text-gray-900"
                                rows={3}
                                placeholder="Enter symptoms..."
                                value={patientData.symptoms}
                                onChange={(e) => setPatientData(prev => ({...prev, symptoms: e.target.value}))}
                            />
                        </div>
                        <div>
                             <label className="flex items-center gap-2 text-lg font-bold text-gray-600 mb-2">
                                <Building size={20} className="text-[#00796B]" /> Previous hospital (optional)
                            </label>
                            <ModernInput 
                                placeholder="Type hospital name" 
                                value={patientData.existingHospital}
                                onChange={(e) => setPatientData(prev => ({...prev, existingHospital: e.target.value}))}
                                className="!text-2xl !font-black !h-16"
                            />
                        </div>
                    </ModernCard>
                </section>
              </div>

              {/* Bottom Action */}
              <div className="fixed bottom-0 left-0 right-0 p-5 bg-white border-t border-gray-100 safe-area-bottom shadow-[0_-4px_20px_rgba(0,0,0,0.05)] z-10">
                 <div className="max-w-md mx-auto flex items-center gap-4">
                    {patientData.ktasLevel && (
                        <div className={cn(
                            "px-5 py-3 rounded-2xl font-black text-center min-w-[100px] shadow-lg border-2",
                            patientData.ktasLevel <= 2 ? "bg-red-600 text-white border-red-700" : "bg-yellow-400 text-black border-yellow-500"
                        )}>
                            <div className="text-xs uppercase opacity-90 tracking-widest mb-1">KTAS</div>
                            <div className="text-4xl leading-none">{patientData.ktasLevel}</div>
                        </div>
                    )}
                    <ModernButton onClick={() => setView('list')} className="flex-1 shadow-lg shadow-teal-200 h-16 text-2xl" size="lg">
                        병원 추천 받기
                    </ModernButton>
                 </div>
              </div>
            </motion.div>
          )}

          {/* VIEW: LIST (Hospitals) */}
          {view === 'list' && (
            <motion.div 
              key="list" 
              className="flex-1 overflow-y-auto p-4 pb-8 bg-[#F5F7FA]"
              initial={{ x: 20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} exit={{ x: -20, opacity: 0 }}
            >
              <div className="flex items-center gap-2 mb-6">
                <div className="p-2 bg-red-50 rounded-lg">
                    <Send size={24} className="text-[#C0392B]" />
                </div>
                <h2 className={TEXT_TITLE}>추천 병원 (Top 3)</h2>
              </div>

              {isLoadingHospitals ? (
                  <div className="flex flex-col items-center justify-center h-64 text-gray-400">
                      <Loader2 className="animate-spin mb-2" size={32} />
                      <p>병원 정보를 불러오는 중...</p>
                  </div>
              ) : hospitals.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-64 text-gray-400 text-center">
                  <p className="font-bold text-lg mb-2">추천 가능한 병원이 없습니다.</p>
                  <p className="text-sm">KTAS 등급과 증상을 입력하면 추천을 받을 수 있습니다.</p>
                </div>
              ) : (
                <div className="space-y-4">
                    {hospitals.map((hospital, idx) => (
                    <ModernCard 
                        key={hospital.id} 
                        // Make the entire card clickable
                        onClick={() => handleHospitalSelect(hospital)}
                        className={cn(
                            "group active:scale-[0.98] transition-all relative overflow-hidden border-2 cursor-pointer shadow-md hover:shadow-xl",
                            idx === 0 ? "border-yellow-400 bg-yellow-50/50" :
                            idx === 1 ? "border-slate-300 bg-slate-50/50" :
                            "border-orange-200 bg-orange-50/50"
                        )}
                    >
                        {/* Rank Badge */}
                        <div className={cn(
                            "absolute top-0 right-0 px-4 py-2 rounded-bl-2xl font-black text-sm z-10 flex items-center gap-1",
                            idx === 0 ? "bg-yellow-400 text-yellow-900" :
                            idx === 1 ? "bg-slate-400 text-white" :
                            "bg-orange-300 text-orange-900"
                        )}>
                            {idx === 0 && <Trophy size={14} />}
                            {idx === 1 && <Medal size={14} />}
                            {idx === 2 && <Medal size={14} />}
                            {idx === 0 ? "1순위" : `${idx + 1}순위`}
                        </div>
                        
                        <div className="flex justify-between items-start mb-4 pr-16">
                            <div>
                                <h3 className="text-2xl font-black text-gray-900 mb-1 leading-tight">{hospital.name}</h3>
                                <div className="flex items-center gap-2 text-sm text-gray-600 font-bold">
                                    <span className="px-2 py-0.5 bg-white border border-gray-200 rounded text-xs text-gray-500">{hospital.specialties?.[0]}</span>
                                    <span>|</span>
                                    <span>커버리지 {hospital.acceptanceRate ?? '--'}%</span>
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-3 gap-2 mb-5">
                            <div className="bg-white/80 p-2 rounded-xl text-center border border-gray-100 shadow-sm">
                                <p className="text-[10px] text-gray-500 font-bold uppercase mb-0.5">가용 병상</p>
                                <p className="text-xl font-black text-[#388E3C]">{hospital.availableBeds}</p>
                            </div>
                            <div className="bg-white/80 p-2 rounded-xl text-center border border-gray-100 shadow-sm">
                                <p className="text-[10px] text-gray-500 font-bold uppercase mb-0.5">예상 시간</p>
                                <p className="text-xl font-black text-[#00796B]">{hospital.eta != null ? `${hospital.eta}분` : '-'}</p>
                            </div>
                            <div className="bg-white/80 p-2 rounded-xl text-center border border-gray-100 shadow-sm">
                                <p className="text-[10px] text-gray-500 font-bold uppercase mb-0.5">거리</p>
                                <p className="text-xl font-black text-[#00796B]">{hospital.distance != null ? `${hospital.distance}km` : '-'}</p>
                            </div>
                        </div>

                        <div className="flex items-center gap-3">
                            {/* Call Button - Icon Only, Distinct Color */}
                            <button 
                                className={cn(
                                  "w-16 h-16 rounded-2xl text-white flex items-center justify-center shadow-lg active:scale-90 transition-all border-2 z-20",
                                  hospital.phoneNumber ? "bg-green-500 border-green-600 active:bg-green-600" : "bg-gray-300 border-gray-300 cursor-not-allowed"
                                )}
                                onClick={(e) => {
                                    e.stopPropagation();
                                    if (!hospital.phoneNumber) return;
                                    window.location.href = `tel:${hospital.phoneNumber}`;
                                }}
                                disabled={!hospital.phoneNumber}
                            >
                                <Phone size={32} fill="currentColor" />
                            </button>

                            {/* Request Button (Visual only since card is clickable, but helpful affordance) */}
                            <div className="flex-1 h-16 bg-blue-600 rounded-2xl flex items-center justify-between px-6 text-white shadow-lg border-2 border-blue-700 group-active:bg-blue-700 transition-colors">
                                <span className="text-xl font-black">수송 요청 보내기</span>
                                <div className="bg-white/20 p-2 rounded-full">
                                    <ChevronRight size={24} className="group-hover:translate-x-1 transition-transform" />
                                </div>
                            </div>
                        </div>
                    </ModernCard>
                    ))}
                </div>
              )}
            </motion.div>
          )}
          {/* VIEW: CONFIRMATION & TRANSFER */}
          {(view === 'confirm' || view === 'transferring' || view === 'completed') && (
            <motion.div 
              key="confirm" 
              className="flex-1 flex flex-col p-6 bg-white"
              initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
            >
              {requestStatus === 'waiting' && view === 'confirm' ? (
                 <div className="flex-1 flex flex-col items-center justify-center text-center">
                    <div className="relative mb-8">
                       <div className="absolute inset-0 bg-yellow-100 rounded-full blur-xl opacity-60 animate-pulse"></div>
                       <div className="relative bg-white p-6 rounded-full shadow-lg border-2 border-yellow-100">
                          <Clock size={48} className="text-yellow-600 animate-spin-slow" />
                       </div>
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">병원 수용 확인 중</h2>
                    <p className="text-gray-500">{selectedHospital?.name} 응급실에<br/>연결하고 있습니다.</p>
                 </div>
              ) : ((requestStatus === 'approved' || requestStatus === 'rejected') && view === 'confirm') ? (
                requestStatus === 'rejected' ? (
                    <div className="flex-1 flex flex-col items-center justify-center text-center">
                        <div className="p-4 bg-red-50 rounded-full mb-6 ring-8 ring-red-50/50">
                            <X size={64} className="text-[#C0392B]" />
                        </div>
                        <h2 className="text-3xl font-bold text-[#C0392B] mb-2">이송 거절됨</h2>
                        <p className="text-gray-600 font-medium text-lg">다른 병원을 선택해주세요.</p>
                        <ModernButton variant="primary" size="full" onClick={() => setView('list')} className="mt-8">
                            목록으로 돌아가기
                        </ModernButton>
                    </div>
                ) : (
                 <div className="flex-1 flex flex-col h-full">
                    <div className="flex-1 flex flex-col items-center justify-center text-center mb-8">
                        <div className="p-4 bg-green-50 rounded-full mb-6 ring-8 ring-green-50/50">
                            <CheckCircle2 size={64} className="text-[#388E3C]" />
                        </div>
                        <h2 className="text-3xl font-bold text-[#388E3C] mb-2">이송 승인 완료</h2>
                        <p className="text-gray-600 font-medium text-lg">{selectedHospital?.name}</p>
                    </div>

                    <ModernCard className="mb-6 bg-gray-50 border-gray-100">
                        <div className="flex justify-between items-center mb-4 pb-4 border-b border-gray-200">
                             <span className="text-gray-500 font-medium">예상 도착</span>
                             <span className="text-xl font-bold text-[#00796B]">{selectedHospital?.eta}분 후</span>
                        </div>
                         <div className="flex justify-between items-center">
                             <span className="text-gray-500 font-medium">확보 병상</span>
                             <span className="text-xl font-bold text-[#388E3C]">{selectedHospital?.availableBeds}개</span>
                        </div>
                    </ModernCard>

                    <div className="mt-auto">
                        <ModernButton variant="success" size="full" onClick={handleStartTransfer} className="shadow-lg shadow-green-200 text-lg py-5 animate-pulse">
                            이송 시작
                        </ModernButton>
                    </div>
                 </div>
                )
              ) : view === 'transferring' ? (
                 <div className="flex-1 flex flex-col items-center justify-center text-center">
                    <div className="relative mb-8">
                       <div className="absolute inset-0 bg-blue-100 rounded-full blur-2xl opacity-60 animate-pulse"></div>
                       <div className="relative bg-white p-8 rounded-full shadow-lg border-4 border-blue-100">
                          <Siren size={64} className="text-blue-600 animate-pulse" />
                       </div>
                    </div>
                    <h2 className="text-3xl font-bold text-gray-900 mb-4">이송 중입니다</h2>
                    <p className="text-xl text-[#00796B] font-bold mb-8">
                        {selectedHospital?.name}
                    </p>
                    <div className="flex items-center gap-2 text-gray-500 bg-gray-100 px-4 py-2 rounded-full">
                        <Navigation size={18} className="animate-bounce" />
                        <span>GPS 경로 안내 중...</span>
                    </div>
                 </div>
              ) : view === 'completed' ? (
                 <div className="flex-1 flex flex-col items-center justify-center text-center h-full">
                    <div className="mb-8">
                        <div className="p-6 bg-gray-800 rounded-full mb-6 ring-8 ring-gray-100">
                            <CheckCircle2 size={64} className="text-white" />
                        </div>
                        <h2 className="text-3xl font-bold text-gray-900 mb-2">이송 완료</h2>
                        <p className="text-gray-500 text-lg">환자가 병원에 안전하게<br/>도착했습니다.</p>
                    </div>

                    <div className="w-full mt-auto">
                        <ModernButton 
                            variant="primary" 
                            size="full" 
                            onClick={handleReset} 
                            className="shadow-lg flex items-center gap-3"
                        >
                            <RotateCcw size={20} />
                            새로운 환자 입력하기
                        </ModernButton>
                    </div>
                 </div>
              ) : null}
            </motion.div>
          )}

        </AnimatePresence>
      </main>
    </div>
  );
};
