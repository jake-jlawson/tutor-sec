/**
 * JobListing.js
 * 
 * This script handles the job listing functionality.
 */

/** FUNCTION: fetchJobs
 * function fetches the jobs from the Flask server.
 * @returns {array} jobs - The array of jobs to be displayed.
 */
async function fetchJobs(params) {
    const options = { // request options
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
    }

    // fetch the jobs from the Flask server
    try {
        const response = await fetch('/app_routes/retrieve_jobs', options);

        if (!response.ok) {
            throw new Error('Failed to fetch jobs');
        }

        const data = await response.json();
        return data;

    } catch (error) {
        console.error('Error fetching jobs:', error);
    }
}


/** FUNCTION: generateJobsList
 * function generates the job listings on the jobs page using the data from the Flask server.
 * @param {string} jobListingContainerId - The ID of the container that contains the job listings.
 * @param {array} jobs - The array of jobs to be displayed.
 */
function generateJobsList(jobListingContainerId, jobs) {
    const jobsContainer = document.getElementById(jobListingContainerId); // get the container for the job listings

    jobs.forEach(job => {
        // Create a job card element
        const jobCard = document.createElement('div');
        jobCard.className = 'card row mb-3 mt-3 ml-0 mr-0';

        jobCard.innerHTML = `
            <div class="card-header d-flex justify-content-between align-items-center" 
                style="color: #000;"
            >
                <div class="d-flex align-items-center">
                    <p class="lead m-0" style="font-size: 13px;"><b>£${job.pay}/hour</b></p>
                    <div class="spacer" style="width: 10px;"></div>
                    <p class="lead m-0" style="font-size: 15px;"><b>⦁</b></p>
                    <div class="spacer" style="width: 10px;"></div>
                    ${job.title}
                    <div class="spacer" style="width: 10px;"></div>
                    <span class="badge bg-${formatOrg(job.company)}">${job.company}</span>
                    <div class="spacer" style="width: 10px;"></div>
                    
                </div>
                <div class="float-end">
                    <a href="#" class="btn btn-primary btn-sm">Apply</a>
                    <a href="#" class="btn btn-outline-danger btn-sm">Reject</a>
                </div>
            </div>

            <div class="card-body">
                <em>
                    <p class="card-text" style="font-size: 12px;">
                        ${formatJobText(job.job_text)}
                    </p>
                </em>
            </div>
        `;

        // Append the job card to the container
        jobsContainer.appendChild(jobCard);
    })
}


/**
 * FORMATTING FUNCTIONS
 */
function formatOrg(company) {
    return company.replaceAll(' ', '');
}

function formatJobText(jobText) {
    const formattedText = jobText
        .replace(/subject:/i, '<br>Subject:')
        .replace(/student profile:/i, '<br>Student Profile:')
        .replace(/feedback report:/i, '<br>Feedback report:')
        .replace(/total hours:/i, '<br>Total hours:')
        .replace(/student time zone:/i, '<br>Student time zone:')
        .replace(/student available time:/i, '<br>Student available time:')
        .replace(/availability:/i, '<br>Availability:')
        .replace(/course content:/i, '<br>Course content:')
        .replace(/platform:/i, '<br>Platform:')
        .replace(/first time:/i, '<br>First time:')
        .replace(/second time:/i, '<br>Second time:')
        .replace(/third time:/i, '<br>Third time:')
        .replace(/fourth time:/i, '<br>Fourth time:')
        .replace(/fifth time:/i, '<br>Fifth time:')
        .replace(/sixth time:/i, '<br>Sixth time:')
        .replace(/seventh time:/i, '<br>Seventh time:')
        .replace(/eighth time:/i, '<br>Eighth time:')
        .replace(/location:/i, '<br>Location:')
        .replace(/preferred time to take the sessions:/i, '<br>Preferred time to take the sessions:')
        .replace(/student based in:/i, '<br>Student based in:')
        .replace(".", '.<br>')

    return formattedText;
}
