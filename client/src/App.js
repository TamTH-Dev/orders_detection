import React, { useState } from 'react'
import axios from 'axios'

import './App.css'

const App = () => {
  const [image, setImage] = useState(null)

  const handleImageChange = (e) => {
    setImage(e.target.files[0])
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      let form_data = new FormData()
      form_data.append('image', image, image.name)
      await axios.post('http://localhost:5000/upload-image', form_data, {
        headers: {
          'content-type': 'multipart/form-data',
        },
      })
    } catch (err) {
      console.log(err)
    }
  }

  return (
    <div className="App">
      <form onSubmit={handleSubmit}>
        <p>
          <input
            type="file"
            id="image"
            accept="image/png, image/jpeg, image/jpg"
            onChange={handleImageChange}
            required
          />
        </p>
        <input type="submit" />
      </form>
    </div>
  )
}

export default App
