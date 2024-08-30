function sendRequest() {
    const userInput = document.getElementById('userInput').value;
    const responseArea = document.getElementById('responseArea');
    const flowchartContainer = document.getElementById('flowchartContainer');
    const loading = document.getElementById('loading');

    // Show the loading symbol
    loading.style.display = 'block';
    responseArea.innerText = ''; // Clear previous response
    flowchartContainer.innerHTML = '';

    fetch('/webhook', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            queryResult: {
                queryText: userInput,
                // Modify this part based on how you determine the intent from user input
                intent: { displayName: userInput.includes('?') ? 'GenerateAdvice' : 'ChooseMajor' },
                parameters: { Major: userInput }
            }
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
        responseArea.innerText = data.fulfillmentMessages[0].text.text[0];
        loading.style.display = 'none'; // Hide the loading symbol

        const semesters = data.fulfillmentMessages[1].flowchartData;
        createFlowchart(semesters);
    })
    .catch((error) => {
        console.error('Error:', error);
        responseArea.innerText = "Error processing your request.";
        loading.style.display = 'none'; // Hide the loading symbol
    });
}

// Function to create the flowchart
function createFlowchart(semesters) {
    const container = document.getElementById('flowchartContainer');
    jsPlumb.setContainer(container);

    const posX = 50, posY = 50;
    const initialPosX = 50; // Initial horizontal position
    const initialPosY = 50; // Initial vertical position
    const verticalSpacing = 200; // Space between semesters vertically
    const horizontalSpacing = 300; // Space between semesters horizontally
    let lastElem = null;

    Object.keys(semesters).forEach((semester, index) => {
        const semesterDiv = document.createElement('div');
        semesterDiv.id = `semester-${index}`;
        semesterDiv.className = 'semester-box';
        semesterDiv.style.position = 'absolute';
        // semesterDiv.style.top = `${posY * index + 10}px`;
        // semesterDiv.style.left = `${posX}px`;
        semesterDiv.style.top = `${initialPosY + index * verticalSpacing}px`; // Position based on index
        semesterDiv.style.left = `${initialPosX + index * horizontalSpacing}px`; // Horizontal positioning
        semesterDiv.style.padding = '10px';
        semesterDiv.style.backgroundColor = '#fff';
        semesterDiv.style.border = '1px solid #A00403';
        semesterDiv.style.borderRadius = '5px';
        semesterDiv.innerHTML = `<b>${semester}</b><br>${semesters[semester].join('<br>')}`;
        container.appendChild(semesterDiv);

        // Create a title for the semester
        let semesterContent = `<b>${semester}</b><br>`;

        // Loop through courses in the semester and display the course details
        semesters[semester].forEach(course => {
            const courseName = course.course_name;
            const courseCode = course.course_code;
            const prerequisites = course.prerequisites && course.prerequisites.length > 0
                ? course.prerequisites.join(', ')
                : 'None';
            
            semesterContent += `${courseName} (Prerequisites: ${prerequisites})<br>`;
        });

        semesterDiv.innerHTML = semesterContent; // Add the semester and course details to the div
        container.appendChild(semesterDiv); // Append the semester div to the flowchart container

        // Make elements draggable
        jsPlumb.draggable(semesterDiv);

        if (lastElem) {
            jsPlumb.connect({
                source: lastElem,
                target: semesterDiv,
                anchors: ["Bottom", "Top"],
                endpoint: "Dot",
                connector: "Straight",
                paintStyle: { stroke: "#A00403", strokeWidth: 2 }
            });
        }
        lastElem = semesterDiv;
    });
}
