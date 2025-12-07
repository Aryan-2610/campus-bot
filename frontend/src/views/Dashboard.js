import React from 'react';
import {
  Box,
  Paper,
  Typography,
  CircularProgress,
  Grid,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

// --- FIX: Created a local PageTitle component to resolve the import error ---
const PageTitle = ({ title, subtitle }) => (
  <Box mb={4}>
    <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
      {title}
    </Typography>
    <Typography variant="subtitle1" color="text.secondary">
      {subtitle}
    </Typography>
  </Box>
);

// --- FIX: Mocked API functions to resolve the import error and provide sample data ---
const getDashboardStats = async () => {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 500));
  // Simulate fetching real-time data by generating random numbers
  return {
    data: {
      conversationCount: Math.floor(Math.random() * 2000) + 1000,
      totalUsers: Math.floor(Math.random() * 800) + 200,
      totalDocuments: Math.floor(Math.random() * 50) + 20,
    },
  };
};

const getConversations = async () => {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 500));
  // Generate some sample conversation data for the last 7 days
  const conversations = [];
  const languages = ['English', 'Hindi', 'Rajasthani', 'Gujarati', 'Telugu'];
  for (let i = 6; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const count = Math.floor(Math.random() * 30) + 10; // Random count between 10 and 40
    for (let j = 0; j < count; j++) {
      conversations.push({
        timestamp: date.toISOString(),
        language: languages[Math.floor(Math.random() * languages.length)],
      });
    }
  }
  return { data: { conversations } };
};

/**
 * The Analytics Dashboard provides a visual overview of bot performance.
 * It fetches conversation data and displays it in various charts and lists.
 */
const Dashboard = () => {
  const [loading, setLoading] = React.useState(true);
  const [stats, setStats] = React.useState({});
  const [conversationData, setConversationData] = React.useState([]);
  const [faqCategoryData, setFaqCategoryData] = React.useState([]);
  const [languageData, setLanguageData] = React.useState([]);

  const clusteredFaqData = [
    [
      {
        "type": "placement cordinator",
        "ques": "What are the eligibility criteria for placement and the placement coordinator role?",
        "ans": "To be eligible for campus recruitment or the Placement Coordinator role, you need a minimum CGPA of 7.0 or above, no history of backlogs, and a minimum of 70% in both 10th and 12th grade.  Placement Coordinators must also have a clean disciplinary record and obtain prior permission from the Training and Placement department for internships and off-campus jobs.  A PC securing a full-time job offer will not be permitted to undertake a six-month internship.",
        "num_sentences": 10
      },
      {
        "type": "fees",
        "ques": "What is the annual fee and deadline for payment without late fees for students?",
        "ans": "The annual academic fee for lateral entry students is Rs. 1,52,700. The last date to pay the annual academic fee for the academic year 2025-26 without a fine has been extended to September 4, 2025.",
        "num_sentences": 15
      },
      {
        "type": "academic",
        "ques": "What is the status of upcoming academic events and how are students informed of any changes?",
        "ans": "The date of the next convocation ceremony is yet to be announced.  The Research and Innovation Excellence Award Ceremony, originally scheduled for September 8th, 2025, has been postponed, with a new date to be announced soon.  Students are informed of major academic event postponements through official notices posted on university notice boards.  Information about upcoming academic events is also published on the university notice boards.",
        "num_sentences": 3
      },
      {
        "type": "placement",
        "ques": "What are the university's policies regarding student involvement with external job agencies and obtaining necessary approvals for off-campus jobs?",
        "ans": "University policy prohibits Placement Coordinators from involvement with external placement consultancies or unauthorized job referrals.  The Department of Training and Placement (T&P) issues No Objection Certificates (NOCs) for off-campus job applications.",
        "num_sentences": 8
      }
    ]
  ];

  React.useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // --- Fetching data from mocked API functions ---
        const statsRes = await getDashboardStats();
        setStats(statsRes.data);

        const convosRes = await getConversations();
        const allConversations = convosRes.data.conversations;

        // --- Data Processing for Charts and Lists ---

        // 1. Conversation Volume over time
        const dailyCounts = allConversations.reduce((acc, convo) => {
          const date = new Date(convo.timestamp).toLocaleDateString();
          acc[date] = (acc[date] || 0) + 1;
          return acc;
        }, {});
        const processedVolume = Object.keys(dailyCounts).map(date => ({
          date,
          count: dailyCounts[date],
        })).sort((a, b) => new Date(a.date) - new Date(b.date));
        setConversationData(processedVolume);

        // 2. Data Processing for FAQ Categories from the JSON
        const categoryCounts = clusteredFaqData[0].reduce((acc, item) => {
          acc[item.type] = (acc[item.type] || 0) + item.num_sentences;
          return acc;
        }, {});
        const processedCategoryData = Object.keys(categoryCounts).map(type => ({
          type: type,
          count: categoryCounts[type],
        })).sort((a, b) => b.count - a.count);
        setFaqCategoryData(processedCategoryData);

        // 3. Data processing for Language Distribution
        const languageCounts = allConversations.reduce((acc, convo) => {
          const lang = convo.language || 'en-US'; // Default to en-US if not present
          acc[lang] = (acc[lang] || 0) + 1;
          return acc;
        }, {});
        const processedLanguageData = Object.keys(languageCounts).map(name => ({
          name,
          value: languageCounts[name],
        }));
        setLanguageData(processedLanguageData);


      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#AF19FF'];

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box p={3}>
      <PageTitle
        title="Bot Analytics Dashboard"
        subtitle="Get a quick overview of your chatbot's performance"
      />
      <Grid container spacing={4} mt={1}>
        {/* Stat Cards Section */}
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <Typography variant="h4" fontWeight="bold" color="primary">{stats.conversationCount}</Typography>
            <Typography color="text.secondary" textAlign="center">Total Conversations</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <Typography variant="h4" fontWeight="bold" color="primary">{stats.totalUsers}</Typography>
            <Typography color="text.secondary" textAlign="center">Total Users</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <Typography variant="h4" fontWeight="bold" color="primary">{stats.totalDocuments}</Typography>
            <Typography color="text.secondary" textAlign="center">Total Documents</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <Typography variant="h4" fontWeight="bold" color="primary">-</Typography>
            <Typography color="text.secondary" textAlign="center">Unanswered Questions</Typography>
          </Paper>
        </Grid>

        {/* Conversation Volume Chart */}
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Conversation Volume</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={conversationData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="count" stroke="#8884d8" name="Conversations" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* FAQ Categories Chart */}
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>FAQ Categories</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={faqCategoryData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="type" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#82ca9d" name="Number of Sentences" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Query Language Distribution Chart */}
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Query Language Distribution</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={languageData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                  nameKey="name"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {languageData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;

