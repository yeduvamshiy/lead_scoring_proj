import React, { useState, useEffect } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import '../App.css';

const coreDesignations = [
    "C-Level Executives",
    "Vice Presidents of Support or Customer Success",
    "Other Vice Presidents",
    "Directors of Support or Customer Success",
    "Other Directors",
    "Managers of Support or Customer Success",
    "Other Managers",
    "Sales Roles",
    "Other Roles",
    "Vice President of Product",
    "Vice President of Engineering",
    "Head of Product",
    "Head of Engineering",
    "Engineering Manager",
    "Product Manager",
    "Founder/Co-founder"
];

const UpdateWeights = () => {
    const [weights, setWeights] = useState({
        "ICP1": {
            "range_50_200": parseFloat(localStorage.getItem('ICP1_range_50_200')) || 1,
            "range_200_500": parseFloat(localStorage.getItem('ICP1_range_200_500')) || 1.2,
            "range_500_100000": parseFloat(localStorage.getItem('ICP1_range_500_100000')) || 1.5,
        },
        "ICP2": {
            "range_50_200": parseFloat(localStorage.getItem('ICP2_range_50_200')) || 0.5,
            "range_200_500": parseFloat(localStorage.getItem('ICP2_range_200_500')) || 0.6,
            "range_500_100000": parseFloat(localStorage.getItem('ICP2_range_500_100000')) || 0.75,
        },
        "designation_scores": coreDesignations.reduce((obj, designation) => {
            obj[designation] = parseFloat(localStorage.getItem(designation)) || (designation.includes("President") ? 1.5 : (designation.includes("Manager") ? 0.5 : 0.1));
            return obj;
        }, {}),
        "engagement_scores": {
            "yes": parseFloat(localStorage.getItem('engagement_yes')) || 1,
            "no": parseFloat(localStorage.getItem('engagement_no')) || 0
        }
    });

    useEffect(() => {
        for (const [key, value] of Object.entries(weights.designation_scores)) {
            localStorage.setItem(key, value);
        }
        for (const [key, value] of Object.entries(weights.ICP1)) {
            localStorage.setItem(`ICP1_${key}`, value);
        }
        for (const [key, value] of Object.entries(weights.ICP2)) {
            localStorage.setItem(`ICP2_${key}`, value);
        }
        for (const [key, value] of Object.entries(weights.engagement_scores)) {
            localStorage.setItem(`engagement_${key}`, value);
        }
    }, [weights]);

    const handleWeightChange = (category, key, newWeight) => {
        setWeights({ ...weights, [category]: { ...weights[category], [key]: parseFloat(newWeight) } });
    };

    const handleSubmit = () => {
        axios.post('http://localhost:5000/update_weights', {
            ICP1: weights.ICP1,
            ICP2: weights.ICP2,
            designation_scores: weights.designation_scores,
            engagement_scores: weights.engagement_scores
        })
            .then(response => {
                alert('Weights updated successfully');
            })
            .catch(error => {
                alert('Error updating weights');
                console.error(error);
            });
    };

    return (
        <div className="container mt-5">
            <h1 className="mb-4">Update Weights</h1>
            <div className="row">
                <div className="col-md-6">
                    <h3>ICP1 Employee Count Scores</h3>
                    {Object.keys(weights.ICP1).map((key) => (
                        <div className="mb-3" key={`ICP1_${key}`}>
                            <label>{key.replace(/_/g, ' ')}: </label>
                            <input
                                type="number"
                                className="form-control"
                                value={weights.ICP1[key]}
                                onChange={(e) => handleWeightChange('ICP1', key, e.target.value)}
                            />
                        </div>
                    ))}
                </div>
                <div className="col-md-6">
                    <h3>ICP2 Employee Count Scores</h3>
                    {Object.keys(weights.ICP2).map((key) => (
                        <div className="mb-3" key={`ICP2_${key}`}>
                            <label>{key.replace(/_/g, ' ')}: </label>
                            <input
                                type="number"
                                className="form-control"
                                value={weights.ICP2[key]}
                                onChange={(e) => handleWeightChange('ICP2', key, e.target.value)}
                            />
                        </div>
                    ))}
                </div>
            </div>
            <h3 className="mt-4">Designation Scores</h3>
            {coreDesignations.map(designation => (
                <div className="mb-3" key={designation}>
                    <label>{designation}: </label>
                    <input
                        type="number"
                        className="form-control"
                        step="0.1"
                        value={weights.designation_scores[designation]}
                        onChange={(e) => handleWeightChange('designation_scores', designation, e.target.value)}
                    />
                </div>
            ))}
            <h3 className="mt-4">Engagement Scores</h3>
            <div className="mb-3">
                <label>Engagement Yes: </label>
                <input
                    type="number"
                    className="form-control"
                    step="0.1"
                    value={weights.engagement_scores["yes"]}
                    onChange={(e) => handleWeightChange('engagement_scores', "yes", e.target.value)}
                />
            </div>
            <div className="mb-3">
                <label>Engagement No: </label>
                <input
                    type="number"
                    className="form-control"
                    step="0.1"
                    value={weights.engagement_scores["no"]}
                    onChange={(e) => handleWeightChange('engagement_scores', "no", e.target.value)}
                />
            </div>
            <button className="btn btn-primary mt-4" onClick={handleSubmit}>Update Weights</button>
        </div>
    );
};

export default UpdateWeights;
