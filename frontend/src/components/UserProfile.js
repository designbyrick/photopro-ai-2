import React, { useState } from 'react';
import { creditAPI } from '../services/api';
import toast from 'react-hot-toast';
import { 
  User, 
  Mail, 
  Calendar, 
  Coins, 
  Crown,
  CreditCard,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

const PLANS = [
  {
    id: 'free',
    name: 'Free',
    credits: 3,
    price: '$0',
    features: ['3 free credits', 'Basic styles'],
    current: true
  },
  {
    id: 'pro',
    name: 'Pro',
    credits: 50,
    price: '$19',
    features: ['50 credits', 'All styles', 'Priority processing'],
    current: false
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    credits: 999,
    price: '$99',
    features: ['999 credits', 'All styles', 'Priority processing', 'Bulk generation'],
    current: false
  }
];

function UserProfile({ user, onCreditsUpdate }) {
  const [loading, setLoading] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);

  const handlePlanPurchase = async (planId) => {
    if (user.plan === planId) {
      toast.error('You are already on this plan');
      return;
    }

    setLoading(true);
    try {
      const response = await creditAPI.purchase({ plan: planId });
      toast.success(response.data.message);
      onCreditsUpdate();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Purchase failed');
    } finally {
      setLoading(false);
      setSelectedPlan(null);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="space-y-8">
      {/* User Info */}
      <div className="text-center">
        <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
          <User className="w-10 h-10 text-white" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900">{user.full_name}</h2>
        <p className="text-gray-600">@{user.username}</p>
        <p className="text-gray-500">{user.email}</p>
      </div>

      {/* Account Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-50 rounded-lg p-4 text-center">
          <Coins className="w-8 h-8 text-yellow-500 mx-auto mb-2" />
          <h3 className="font-semibold text-gray-900">{user.credits}</h3>
          <p className="text-sm text-gray-600">Credits</p>
        </div>
        
        <div className="bg-gray-50 rounded-lg p-4 text-center">
          <Crown className="w-8 h-8 text-purple-500 mx-auto mb-2" />
          <h3 className="font-semibold text-gray-900 capitalize">{user.plan}</h3>
          <p className="text-sm text-gray-600">Plan</p>
        </div>
        
        <div className="bg-gray-50 rounded-lg p-4 text-center">
          <Calendar className="w-8 h-8 text-blue-500 mx-auto mb-2" />
          <h3 className="font-semibold text-gray-900">
            {formatDate(user.created_at)}
          </h3>
          <p className="text-sm text-gray-600">Member Since</p>
        </div>
      </div>

      {/* Upgrade Plans */}
      <div>
        <h3 className="text-xl font-bold text-gray-900 mb-6">Upgrade Your Plan</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {PLANS.map((plan) => (
            <div
              key={plan.id}
              className={`relative rounded-lg border-2 p-6 ${
                plan.id === user.plan
                  ? 'border-purple-500 bg-purple-50'
                  : 'border-gray-200 hover:border-purple-300'
              }`}
            >
              {plan.id === user.plan && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <span className="bg-purple-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                    Current Plan
                  </span>
                </div>
              )}
              
              <div className="text-center">
                <h4 className="text-lg font-bold text-gray-900">{plan.name}</h4>
                <div className="mt-2">
                  <span className="text-3xl font-bold text-gray-900">{plan.price}</span>
                  <span className="text-gray-600">/month</span>
                </div>
                <p className="text-sm text-gray-600 mt-1">{plan.credits} credits</p>
              </div>

              <ul className="mt-6 space-y-3">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-center">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                    <span className="text-sm text-gray-600">{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                onClick={() => setSelectedPlan(plan.id)}
                disabled={plan.id === user.plan || loading}
                className={`w-full mt-6 py-2 px-4 rounded-lg font-medium transition-colors ${
                  plan.id === user.plan
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-purple-600 text-white hover:bg-purple-700'
                }`}
              >
                {plan.id === user.plan ? 'Current Plan' : 'Upgrade'}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Purchase Confirmation Modal */}
      {selectedPlan && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="text-center">
              <CreditCard className="w-12 h-12 text-purple-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Confirm Plan Upgrade
              </h3>
              <p className="text-gray-600 mb-6">
                Are you sure you want to upgrade to the {PLANS.find(p => p.id === selectedPlan)?.name} plan?
              </p>
              
              <div className="flex space-x-4">
                <button
                  onClick={() => setSelectedPlan(null)}
                  className="btn btn-secondary flex-1"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handlePlanPurchase(selectedPlan)}
                  disabled={loading}
                  className="btn btn-primary flex-1"
                >
                  {loading ? (
                    <span className="flex items-center justify-center">
                      <span className="spinner mr-2"></span>
                      Processing...
                    </span>
                  ) : (
                    'Confirm'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default UserProfile;
