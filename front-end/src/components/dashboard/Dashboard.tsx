import React,{useState,useEffect} from 'react'
import { NavLink, useNavigate,useParams} from 'react-router-dom'
import LeftDashboard from './LeftDashboard'
import RightDashboard from './RightDashboard'
import axios from 'axios'

const Dashboard = () => {
  const [projectData,setProjectData] = useState([])
  const [cardData, setCardData] = useState([])
  const [overviewData,setOverviewData] = useState({})
  const [selected,setSelected] = useState('')
  let navigate = useNavigate()
  const token = localStorage.getItem('token')
  let id = useParams()
  const handleChange = (e:any) => {
    navigate(`/${e.target.value}`)
    setSelected(e.target.value)
  }

  const fetchProjects = async () => {
    await axios.get(`http://127.0.0.1:5000/projects`, {
      headers: {
        'x-access-token': `${token}`
      }
    })
    .then((res: any) => {
      console.log(
        "project " + res.status
      )
      console.log(res.data)
      if(res.status == 200) {
        const project = res.data
        setProjectData(project)
        if(id == null) {
          navigate(`/${project[0].project_id}`)
          id = project[0].project_id
          
        }
        
      }
      if(res.status == 401) {
        navigate('/login')
        localStorage.clear()
      }
      
    })
  }

  const fetchZoneUsable = async () => {
    await axios.get(`http://127.0.0.1:5000/dashboard/zoneusable/projectid=1`, {
        headers: {
            'x-access-token': `${token}`
        }
    }).then(
        (response) => {
            console.log(response.status)
            if(response.status == 200) {
                setCardData(response.data)
            }
            if(response.status == 401) {
                localStorage.clear()
                navigate('/login')
            }
        },
        (error) => {
            console.log(error)
        }
    )
}

const [totalZone,setTotalZone] = useState()
const [averageSpace,setAverageSpace] = useState()
const [averageRate,setAverageRate] = useState()
const [totalAccessed,setTotalAccessed] = useState()
const [createdOn,setCreatedOn] = useState("")
const fetchOverview = async () => {
  await axios.get(`http://127.0.0.1:5000/dashboard/statistic/projectid=1`, {
      headers: {
          'x-access-token': `${token}`
      }
  }).then(
      (response) => {
          console.log(response.status)
          if(response.status == 200) {
            setOverviewData(response.data)
            setTotalZone(response.data.statistic[0].total_zone)
            setAverageSpace(response.data.statistic[0].average_space)
            setAverageRate(response.data.statistic[0].average_rate)
            setTotalAccessed(response.data.detail[0].total_accessed)
            setCreatedOn(response.data.detail[0].created_on)
          }
      },
      (error) => {
          console.log(error)
      }
  )
}

  useEffect(() => {
    fetchProjects()
    fetchZoneUsable()
    fetchOverview()
  },[])

  return (
    <div className="w-full h-full flex flex-col justify-start item-start px-6 overflow-y-auto">
      <div className='flex w-full justify-between items-center py-6'>
        <span className='text-2xl lg:text-3xl font-bold'>Dashboard</span>
        <select value={selected} onChange={handleChange} className="px-1 md:px-6 py-2 rounded-lg border focus:outline-none cursor-pointer" id="">
          {projectData.map((data)=> (
              <option value={data.project_id}>{data.project_name}</option>
            ))}
        </select>
      </div>
      <div className='grid grid-cols-1 lg:grid-cols-6 w-full gap-10 mb-16'>
        <div className='col-span-1 lg:col-span-4'>
          <LeftDashboard data={cardData} />
        </div>
        <div className='col-span-1 lg:col-span-2'>
          <RightDashboard totalZone={totalZone} averageRate={averageRate} averageSpace={averageSpace} totalAccessed={totalAccessed} createdOn={createdOn}/>
        </div>
      </div>
    </div>
  )
}

export default Dashboard