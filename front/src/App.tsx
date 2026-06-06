import React, { useEffect, useState } from 'react';
import {
  Ambulance,
  ChevronRight,
  Loader2,
  Lock,
  Stethoscope,
  User as UserIcon,
  X,
} from 'lucide-react';
import { AnimatePresence, motion } from 'motion/react';
import { ParamedicDashboard } from './components/ParamedicDashboard';
import { ERTabletDashboard } from './components/ERTabletDashboard';
import { UserRole } from './types';
import {
  LAYOUT_CONTAINER,
  ModernButton,
  ModernCard,
  ModernInput,
  cn,
} from './components/ui/DesignSystem';
import { supabase } from './utils/supabase/client';

interface UserSession {
  id: string;
  role: UserRole;
  name: string;
  hospitalId?: string | null;
}

interface ProfileRow {
  role: string | null;
  name: string | null;
  hospital_id: string | null;
}

const demoAuthEnabled =
  typeof import.meta !== 'undefined' &&
  (import.meta as any).env?.VITE_DEMO_AUTH === 'true';

function withTimeout<T>(promise: Promise<T>, ms: number, label: string): Promise<T> {
  return Promise.race([
    promise,
    new Promise<T>((_, reject) => {
      window.setTimeout(() => reject(new Error(`${label} timeout`)), ms);
    }),
  ]);
}

function getReadableAuthError(error: unknown): string {
  if (error instanceof TypeError && error.message === 'Failed to fetch') {
    return 'Supabase auth server could not be reached. Check internet access, firewall or VPN, ad blocker, and whether the Supabase project is active.';
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'Unknown authentication error';
}

function buildUserSession(
  authUser: { id: string; email?: string | null },
  profile: ProfileRow | null,
): UserSession | null {
  const role = profile?.role;
  if (role !== 'paramedic' && role !== 'hospital') {
    console.warn('Invalid or missing profile role:', role);
    return null;
  }

  if (role === 'hospital' && !profile?.hospital_id) {
    console.warn('Hospital profile is missing hospital_id:', authUser.id);
    return null;
  }

  return {
    id: authUser.id,
    role,
    hospitalId: profile?.hospital_id ?? null,
    name: profile?.name || authUser.email?.split('@')[0] || 'User',
  };
}

export default function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<UserSession | null>(null);

  const [showLoginModal, setShowLoginModal] = useState(false);
  const [selectedRoleForLogin, setSelectedRoleForLogin] = useState<UserRole>(null);
  const [loginId, setLoginId] = useState('');
  const [loginPwd, setLoginPwd] = useState('');
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  useEffect(() => {
    if (demoAuthEnabled) {
      const saved = localStorage.getItem('ems_demo_session');
      if (saved) {
        try {
          setUser(JSON.parse(saved));
        } catch (error) {
          console.warn('Failed to parse demo session:', error);
          localStorage.removeItem('ems_demo_session');
        }
      }
      setIsLoading(false);
      return;
    }

    let isMounted = true;

    const checkSession = async () => {
      try {
        const { data: { session } } = await withTimeout(
          supabase.auth.getSession(),
          4000,
          'Supabase session',
        );

        if (session?.user) {
          const { data: profile } = await supabase
            .from('profiles')
            .select('role, name, hospital_id')
            .eq('id', session.user.id)
            .single();

          const userSession = buildUserSession(session.user, profile);
          if (userSession && isMounted) {
            setUser(userSession);
          }
        }
      } catch (error) {
        console.warn('Initial session check failed:', error);
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    checkSession();

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (!session) {
        setUser(null);
      }
    });

    return () => {
      isMounted = false;
      subscription.unsubscribe();
    };
  }, []);

  const handleLoginStart = (role: UserRole) => {
    setSelectedRoleForLogin(role);
    setLoginId('');
    setLoginPwd('');
    setShowLoginModal(true);
  };

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!loginId || !loginPwd) return;

    setIsLoggingIn(true);

    try {
      if (demoAuthEnabled) {
        const demoUser: UserSession = {
          id: `demo-${selectedRoleForLogin}-${Date.now()}`,
          role: selectedRoleForLogin,
          hospitalId: selectedRoleForLogin === 'hospital' ? 'demo-hospital' : null,
          name: loginId.split('@')[0] || 'demo-user',
        };
        localStorage.setItem('ems_demo_session', JSON.stringify(demoUser));
        setUser(demoUser);
        setShowLoginModal(false);
        return;
      }

      const { data, error } = await withTimeout(
        supabase.auth.signInWithPassword({
          email: loginId,
          password: loginPwd,
        }),
        8000,
        'Sign in',
      );

      if (error) throw error;

      if (data.user) {
        const { data: profile, error: profileError } = await supabase
          .from('profiles')
          .select('role, name, hospital_id')
          .eq('id', data.user.id)
          .single();

        if (profileError || !profile) {
          throw new Error('Profile not found. Ask an administrator to create your profile.');
        }

        const userSession = buildUserSession(data.user, profile);
        if (!userSession) {
          throw new Error('Profile is incomplete or has an unsupported role.');
        }

        const { data: sessionDebug } = await supabase.auth.getSession();
        const { data: userDebug } = await supabase.auth.getUser();
        console.log('[auth-debug] after login', {
          userId: userDebug.user?.id ?? null,
          sessionExists: Boolean(sessionDebug.session),
          accessTokenExists: Boolean(sessionDebug.session?.access_token),
        });

        setUser(userSession);
        setShowLoginModal(false);
      }
    } catch (error) {
      console.error('Auth error:', error);
      alert(`Login failed: ${getReadableAuthError(error)}`);
    } finally {
      setIsLoggingIn(false);
    }
  };

  const handleLogout = async () => {
    if (demoAuthEnabled) {
      localStorage.removeItem('ems_demo_session');
      setUser(null);
      return;
    }

    await supabase.auth.signOut();
    setUser(null);
    localStorage.removeItem('ems_app_session');
  };

  if (isLoading) {
    return (
      <div className={cn(LAYOUT_CONTAINER, 'items-center justify-center')}>
        <Loader2 className="animate-spin text-[#00796B]" size={48} />
      </div>
    );
  }

  if (user) {
    if (user.role === 'paramedic') {
      return <ParamedicDashboard userName={user.name} onLogout={handleLogout} />;
    }
    if (user.role === 'hospital') {
      return <ERTabletDashboard hospitalId={user.hospitalId} onLogout={handleLogout} />;
    }
  }

  return (
    <div className={LAYOUT_CONTAINER}>
      <div className="flex-1 flex flex-col p-8 justify-center relative">
        <div className="flex flex-col items-center text-center mb-12">
          <div className="p-4 bg-red-50 rounded-full mb-6 ring-8 ring-red-50/50">
            <Ambulance size={56} className="text-[#C0392B]" />
          </div>
          <h1 className="text-3xl font-black text-gray-900 leading-tight mb-2 tracking-tight">
            Emergency Patient Transfer
            <br />
            Integrated System
          </h1>
          <p className="text-gray-500 font-bold text-sm tracking-wide">
            ERMCT Emergency Transfer Platform
          </p>
        </div>

        <div className="flex flex-col gap-5 w-full">
          <button
            onClick={() => handleLoginStart('paramedic')}
            className="group relative"
          >
            <ModernCard className="flex items-center p-6 border-2 hover:border-[#C0392B] hover:shadow-lg transition-all group-active:scale-[0.98] text-left">
              <div className="p-4 bg-red-50 rounded-2xl mr-5 group-hover:bg-[#C0392B] transition-colors">
                <Ambulance size={32} className="text-[#C0392B] group-hover:text-white transition-colors" />
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-black text-gray-900 mb-1">Paramedic</h3>
                <p className="text-sm font-medium text-gray-500">Patient input and transfer request</p>
              </div>
              <ChevronRight className="text-gray-300 group-hover:text-[#C0392B] transition-colors" />
            </ModernCard>
          </button>

          <button
            onClick={() => handleLoginStart('hospital')}
            className="group relative"
          >
            <ModernCard className="flex items-center p-6 border-2 hover:border-[#00796B] hover:shadow-lg transition-all group-active:scale-[0.98] text-left">
              <div className="p-4 bg-teal-50 rounded-2xl mr-5 group-hover:bg-[#00796B] transition-colors">
                <Stethoscope size={32} className="text-[#00796B] group-hover:text-white transition-colors" />
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-black text-gray-900 mb-1">Hospital</h3>
                <p className="text-sm font-medium text-gray-500">Receive requests and manage bed status</p>
              </div>
              <ChevronRight className="text-gray-300 group-hover:text-[#00796B] transition-colors" />
            </ModernCard>
          </button>
        </div>

        <AnimatePresence>
          {showLoginModal && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 z-50 bg-white flex flex-col items-center justify-center p-8"
            >
              <div className="w-full max-w-sm">
                <div className="flex justify-between items-center mb-8">
                  <button
                    onClick={() => setShowLoginModal(false)}
                    className="p-2 -ml-2 rounded-full hover:bg-gray-100 text-gray-500"
                  >
                    <X size={24} />
                  </button>
                  <h2 className="text-xl font-black text-gray-900">
                    {selectedRoleForLogin === 'paramedic' ? 'Paramedic Login' : 'Hospital Login'}
                  </h2>
                  <div className="w-8" />
                </div>

                <form onSubmit={handleAuthSubmit} className="flex flex-col gap-5">
                  <div>
                    <label className="block text-sm font-bold text-gray-500 mb-2 uppercase">Email</label>
                    <div className="relative">
                      <UserIcon className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                      <ModernInput
                        placeholder="name@example.com"
                        type="email"
                        className="pl-12"
                        value={loginId}
                        onChange={(e) => setLoginId(e.target.value)}
                        autoFocus
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-bold text-gray-500 mb-2 uppercase">Password</label>
                    <div className="relative">
                      <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                      <ModernInput
                        type="password"
                        placeholder="Enter password"
                        className="pl-12"
                        value={loginPwd}
                        onChange={(e) => setLoginPwd(e.target.value)}
                      />
                    </div>
                  </div>

                  <ModernButton
                    type="submit"
                    disabled={!loginId || !loginPwd || isLoggingIn}
                    className={cn(
                      'mt-4 py-4 text-lg shadow-lg',
                      selectedRoleForLogin === 'paramedic'
                        ? 'bg-[#C0392B] hover:bg-[#A93226] shadow-red-200'
                        : 'bg-[#00796B] hover:bg-[#00695C] shadow-teal-200',
                    )}
                  >
                    {isLoggingIn ? <Loader2 className="animate-spin" /> : 'Login'}
                  </ModernButton>

                  <div className="text-center">
                    <p className="text-sm font-bold text-gray-500">
                      Signup is temporarily disabled. Use a seeded Supabase account.
                    </p>
                  </div>
                </form>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
