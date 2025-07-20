import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Calendar, 
  BarChart3, 
  Users, 
  Clock, 
  TrendingUp, 
  MessageCircle, 
  Heart,
  Share2,
  Eye,
  Zap,
  Plus,
  Settings
} from 'lucide-react';
import Header from '../Layout/Header';
// Assuming these APIs are unified in a single api service or separated by concerns
import { analyticsAPI, contentAPI, socialAccountsAPI } from '../../services/api'; 

const Dashboard = ({ setIsAuth }) => {
  const [stats, setStats] = useState({
    totalPosts: 0,
    scheduledPosts: 0,
    totalEngagement: 0,
    connectedAccounts: 0,
    weeklyGrowth: 0
  });
  const [recentPosts, setRecentPosts] = useState([]);
  const [upcomingPosts, setUpcomingPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [statsRes, recentRes, upcomingRes] = await Promise.all([
        // These will be calls to the unified backend API
        analyticsAPI.getOverviewStats(),
        contentAPI.getRecentPosts(),
        socialAccountsAPI.getUpcomingPosts() // Assuming scheduler or content API provides this
      ]);
      
      setStats(statsRes.data);
      setRecentPosts(recentRes.data);
      setUpcomingPosts(upcomingRes.data);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: 'Total Posts',
      value: stats.totalPosts,
      icon: MessageCircle,
      color: 'from-blue-500 to-cyan-500',
      change: '+12%'
    },
    {
      title: 'Scheduled Posts',
      value: stats.scheduledPosts,
      icon: Clock,
      color: 'from-purple-500 to-pink-500',
      change: '+8%'
    },
    {
      title: 'Total Engagement',
      value: stats.totalEngagement.toLocaleString(),
      icon: Heart,
      color: 'from-green-500 to-emerald-500',
      change: '+23%'
    },
    {
      title: 'Connected Accounts',
      value: stats.connectedAccounts,
      icon: Users,
      color: 'from-orange-500 to-red-500',
      change: '+2'
    }
  ];

  if (loading) {
    return (
      <div className="min-h-screen">
        <Header setIsAuth={setIsAuth} />
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-white"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Header setIsAuth={setIsAuth} />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-2">Welcome back! 👋</h1>
          <p className="text-white/70 text-lg">Here's what's happening with your social media today.</p>
        </motion.div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {statCards.map((card, index) => (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="glass rounded-2xl p-6 hover:bg-white/10 transition-all duration-300"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-xl bg-gradient-to-r ${card.color}`}>
                  <card.icon className="w-6 h-6 text-white" />
                </div>
                <span className="text-green-400 text-sm font-medium">{card.change}</span>
              </div>
              <h3 className="text-2xl font-bold text-white mb-1">{card.value}</h3>
              <p className="text-white/70 text-sm">{card.title}</p>
            </motion.div>
          ))}
        </div>

        {/* Quick Actions */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass rounded-2xl p-6 mb-8"
        >
          <h2 className="text-xl font-bold text-white mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Link 
              to="/scheduler"
              className="flex flex-col items-center p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-all duration-300 group"
            >
              <Calendar className="w-8 h-8 text-blue-400 mb-2 group-hover:scale-110 transition-transform" />
              <span className="text-white text-sm font-medium">Schedule Post</span>
            </Link>
            <Link 
              to="/content"
              className="flex flex-col items-center p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-all duration-300 group"
            >
              <Plus className="w-8 h-8 text-green-400 mb-2 group-hover:scale-110 transition-transform" />
              <span className="text-white text-sm font-medium">Create Content</span>
            </Link>
            <Link 
              to="/analytics"
              className="flex flex-col items-center p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-all duration-300 group"
            >
              <BarChart3 className="w-8 h-8 text-purple-400 mb-2 group-hover:scale-110 transition-transform" />
              <span className="text-white text-sm font-medium">View Analytics</span>
            </Link>
            <Link 
              to="/accounts"
              className="flex flex-col items-center p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-all duration-300 group"
            >
              <Settings className="w-8 h-8 text-orange-400 mb-2 group-hover:scale-110 transition-transform" />
              <span className="text-white text-sm font-medium">Manage Accounts</span>
            </Link>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Posts */}
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
            className="glass rounded-2xl p-6"
          >
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-white">Recent Posts</h2>
              <Link to="/content" className="text-blue-400 hover:text-blue-300 text-sm">
                View All
              </Link>
            </div>
            <div className="space-y-4">
              {recentPosts.length > 0 ? recentPosts.map((post, index) => (
                <div key={index} className="bg-white/5 rounded-xl p-4 hover:bg-white/10 transition-all duration-300">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center">
                        <MessageCircle className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h4 className="text-white font-medium">{post.platform}</h4>
                        <p className="text-white/60 text-sm">{post.date}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-white/70">
                      <div className="flex items-center space-x-1">
                        <Eye className="w-4 h-4" />
                        <span>{post.views}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Heart className="w-4 h-4" />
                        <span>{post.likes}</span>
                      </div>
                    </div>
                  </div>
                  <p className="text-white/80 text-sm line-clamp-2">{post.content}</p>
                </div>
              )) : (
                <div className="text-center py-8">
                  <MessageCircle className="w-12 h-12 text-white/20 mx-auto mb-3" />
                  <p className="text-white/50">No recent posts</p>
                  <Link 
                    to="/scheduler"
                    className="inline-block mt-2 text-blue-400 hover:text-blue-300 text-sm"
                  >
                    Create your first post
                  </Link>
                </div>
              )}
            </div>
          </motion.div>

          {/* Upcoming Posts */}
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.7 }}
            className="glass rounded-2xl p-6"
          >
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-white">Upcoming Posts</h2>
              <Link to="/scheduler" className="text-blue-400 hover:text-blue-300 text-sm">
                Schedule More
              </Link>
            </div>
            <div className="space-y-4">
              {upcomingPosts.length > 0 ? upcomingPosts.map((post, index) => (
                <div key={index} className="bg-white/5 rounded-xl p-4 hover:bg-white/10 transition-all duration-300">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-r from-green-500 to-blue-500 flex items-center justify-center">
                        <Clock className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h4 className="text-white font-medium">{post.platform}</h4>
                        <p className="text-white/60 text-sm">{post.scheduledTime}</p>
                      </div>
                    </div>
                    <span className="bg-green-500/20 text-green-400 text-xs px-2 py-1 rounded-full">
                      Scheduled
                    </span>
                  </div>
                  <p className="text-white/80 text-sm line-clamp-2">{post.content}</p>
                </div>
              )) : (
                <div className="text-center py-8">
                  <Clock className="w-12 h-12 text-white/20 mx-auto mb-3" />
                  <p className="text-white/50">No upcoming posts</p>
                  <Link 
                    to="/scheduler"
                    className="inline-block mt-2 text-blue-400 hover:text-blue-300 text-sm"
                  >
                    Schedule a post
                  </Link>
                </div>
              )}
            </div>
          </motion.div>
        </div>

        {/* Performance Insight */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="glass rounded-2xl p-6 mt-8"
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <TrendingUp className="w-6 h-6 text-green-400" />
              <h2 className="text-xl font-bold text-white">This Week's Growth</h2>
            </div>
            <span className="text-green-400 font-medium">+{stats.weeklyGrowth}%</span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-white mb-1">+1,234</div>
              <div className="text-white/60 text-sm">New Followers</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white mb-1">+5,678</div>
              <div className="text-white/60 text-sm">Impressions</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white mb-1">+234</div>
              <div className="text-white/60 text-sm">Engagements</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white mb-1">+45</div>
              <div className="text-white/60 text-sm">Shares</div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;
