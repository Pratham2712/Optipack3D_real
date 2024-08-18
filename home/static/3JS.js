import * as THREE from 'three';
import { OrbitControls } from '/static/node_modules/three/examples/jsm/controls/OrbitControls.js';
import { FontLoader } from '/static/node_modules/three/examples/jsm/loaders/FontLoader.js';
import { TextGeometry } from '/static/node_modules/three/examples/jsm/geometries/TextGeometry.js';
import { GLTFLoader } from '/static/node_modules/three/examples/jsm/loaders/GLTFLoader.js';

// Renderer setup

document.addEventListener('DOMContentLoaded', () => {
    const threedPath = window.threedPath;
    const containerInfPath = window.containerInfPath;
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xffffff);

    // Camera setup
    const camera = new THREE.PerspectiveCamera(
        70,
        window.innerWidth / window.innerHeight,
        0.1,
        500000
    );
    const orbit = new OrbitControls(camera, renderer.domElement);

    // For making restrictions to the rotation of the camera like they have done in Easy Cargo.
    // orbit.enablePan = false; // Disable panning for simplicity
    // orbit.minPolarAngle = Math.PI / 8; // Minimum polar angle (from top view)
    // orbit.maxPolarAngle = Math.PI / 2.1; // Maximum polar angle (from top view)
    // orbit.minAzimuthAngle = -Infinity; // Minimum azimuth angle
    // orbit.maxAzimuthAngle = Infinity; // Maximum azimuth angle
    // orbit.update();

    const textureLoader = new THREE.TextureLoader();
    const rustyTexture = textureLoader.load('/static/images/rust3.png', function (texture) {
        // Adjust texture wrapping and repeat as needed
        texture.wrapS = THREE.RepeatWrapping;
        texture.wrapT = THREE.RepeatWrapping;
        texture.repeat.set(1, 1); // Adjust these values to control how the texture is repeated
    });

    let containerWidth;
    let containerHeight;
    let containerDepth;

    // Function to initialize container dimensions
    function fetchContainerDimensions() {
        return fetch(containerInfPath)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(containerInfo => {
                containerWidth = containerInfo.containerWidth;
                containerHeight = containerInfo.containerHeight;
                containerDepth = containerInfo.containerLength; // Ensure this field name matches your JSON

                console.log('Container Width (inside fetch):', containerWidth);
                console.log('Container Height (inside fetch):', containerHeight);
                console.log('Container Depth (inside fetch):', containerDepth);

                // Return an object with the dimensions
                return { containerWidth, containerHeight, containerDepth };
            })
            .catch(error => console.error('Error loading container info:', error));
    }

    // Call the function and use the dimensions once fetched


    const aspectWidth = 1; // This is the base aspect (1x)
    const aspectHeight = 1; // Height relative to width
    const aspectDepth = 2;

    fetchContainerDimensions().then(dimensions => {
    

        // Your further logic here, using the dimensions
        const faces = [
            { normal: new THREE.Vector3(1, 0, 0), position: new THREE.Vector3(containerWidth, 0, 0) },    // Right face
            { normal: new THREE.Vector3(-1, 0, 0), position: new THREE.Vector3(-containerWidth, 0, 0) }, // Left face
            { normal: new THREE.Vector3(0, 1, 0), position: new THREE.Vector3(0, containerHeight, 0) },  // Top face
            // { normal: new THREE.Vector3(0, -1, 0), position: new THREE.Vector3(0, -containerHeight, 0) }, // Bottom face
            { normal: new THREE.Vector3(0, 0, 1), position: new THREE.Vector3(0, 0, containerDepth) },    // Front face
            { normal: new THREE.Vector3(0, 0, -1), position: new THREE.Vector3(0, 0, -containerDepth) }   // Back face
        ];

            // Set the target of the OrbitControls to the center of the container
        orbit.target.set((containerWidth / 2)*aspectWidth, (containerHeight / 2)*aspectHeight, (containerDepth / 2)*aspectDepth);
        orbit.update();

        camera.position.set(4.9 * containerWidth*aspectWidth, 4.9 * containerHeight*aspectHeight, 1.2* containerDepth*aspectDepth);
        orbit.update();

        // Axes helper
        const axesHelper = new THREE.AxesHelper(1000);
        scene.add(axesHelper);

        // Container wireframe
        const containerGeometry = new THREE.BoxGeometry(containerWidth, containerHeight, containerDepth);
        const containerEdges = new THREE.EdgesGeometry(containerGeometry);
        const containerMaterial = new THREE.LineBasicMaterial({ color: 0x000, transparent: true, opacity: 0.5 });
        const containerWireframe = new THREE.LineSegments(containerEdges, containerMaterial);

        const plateGeometry = new THREE.BoxGeometry(containerWidth, containerDepth*aspectDepth,200);
        const plateMaterial = new THREE.MeshStandardMaterial({
            // map:rustyTexture, 
            side: THREE.DoubleSide,
            // metalness:0.9,
            color:0xd3d3d3d

        });

        const plateMaterialforSides = new THREE.MeshStandardMaterial({
            map:rustyTexture, 
            side: THREE.DoubleSide,
            metalness:0.9,
            opacity:1,
            color:0xB87333

        });

        const basePlate = new THREE.Mesh(plateGeometry, plateMaterial);

        // Position the base plate at the bottom of the container
        basePlate.rotation.x = Math.PI / 2; // Rotate to make it horizontal
        basePlate.position.set(
            (containerWidth / 2) ,
            -100, // Bottom of the container
            (containerDepth / 2)*aspectDepth 
        );

        scene.add(basePlate);

        // Calculate aspect ratios relative to the container width
        // Depth relative to width

        const plate = new THREE.BoxGeometry(containerWidth, containerHeight * aspectHeight, 100);
        const makeBasePlate = new THREE.Mesh(plate,plateMaterialforSides);
        makeBasePlate.position.set(containerWidth/2,containerHeight/2,-50);
        scene.add(makeBasePlate);


        // Apply scaling to the container wireframe to maintain the aspect ratio
        containerWireframe.scale.set(aspectWidth, aspectHeight, aspectDepth);
        containerWireframe.position.set(
            (containerWidth / 2) * aspectWidth,
            (containerHeight / 2) * aspectHeight,
            (containerDepth / 2) * aspectDepth
        );

        scene.add(containerWireframe);

        
        // Color mapping from names to hex codes
        const colorMap = {
            "red": 0xFF0000,
            "green": 0x00FF00,
            "blue": 0x0000FF,
            "yellow": 0xFFFF00,
            "purple": 0x800080,
            "orange": 0xFFA500,
            "black": 0x000000,
            
        };

        let textMesh; // Declare textMesh globally
        let yPosition; // Store original y position

        // Function to create and place small boxes using coordinates from JSON
        const createSmallBoxesFromCoordinates = (boxes) => {
            boxes.forEach(box => {
                const startX = box.start.x;
                const startZ = containerDepth - box.start.y;
                const startY = box.start.z;

                const endX = box.end.x;
                const endY = box.end.z;
                const endZ = containerDepth - box.end.y;
                const colorName = box.color;

                // colorName = hexTo0x(colorName)
                // console.log(startX)

                const smallBoxWidth = box.dimensions.width;
                const smallBoxHeight = box.dimensions.height;
                const smallBoxDepth = box.dimensions.length;

                const centerX = startX + smallBoxWidth / 2;
                const centerY = startY + smallBoxHeight / 2;
                const centerZ = startZ - smallBoxDepth / 2;

                const smallBoxGeometry = new THREE.BoxGeometry(smallBoxWidth, smallBoxHeight, smallBoxDepth);
                const smallBoxMaterial = new THREE.MeshStandardMaterial({
                    color: parseInt(colorName, 16)|| 0xFFFFFF,
                    transparent: true,
                    opacity: 0.9,
                    side: THREE.DoubleSide
                });
                const smallBox = new THREE.Mesh(smallBoxGeometry, smallBoxMaterial);

                // Apply the same aspect ratio scaling to the small boxes
                smallBox.scale.set(aspectWidth, aspectHeight, aspectDepth);

                // Adjust position to account for scaling
                smallBox.position.set(
                    centerX * aspectWidth,
                    centerY * aspectHeight,
                    centerZ * aspectDepth
                );

                scene.add(smallBox);

                const smallBoxEdges = new THREE.EdgesGeometry(smallBoxGeometry);
                const smallBoxEdgesMaterial = new THREE.LineBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.5 });
                const smallBoxWireframe = new THREE.LineSegments(smallBoxEdges, smallBoxEdgesMaterial);
                // smallBox.scale.set(aspectWidth, aspectHeight, aspectDepth);
                smallBoxWireframe.scale.set(aspectWidth, aspectHeight, aspectDepth);


                // Adjust position to account for scaling
                smallBoxWireframe.position.set(
                    centerX * aspectWidth,
                    centerY * aspectHeight,
                    centerZ * aspectDepth
                );

                scene.add(smallBoxWireframe);
            });
        };

        // Function to add a horizontal line at a given y position
        const addHorizontalLine = (yPosition) => {
            const lineMaterial = new THREE.LineBasicMaterial({ color: 0xFF0000 });
            const lineGeometry = new THREE.BufferGeometry().setFromPoints([
                new THREE.Vector3(0*aspectWidth, 0*aspectHeight, yPosition*aspectDepth),
                new THREE.Vector3(containerWidth*aspectWidth, 0*aspectHeight, yPosition*aspectDepth)
            ]);
            const line = new THREE.Line(lineGeometry, lineMaterial);
            scene.add(line);
        };

        const addVerticalLine = (yPosition) => {
            const lineMaterial = new THREE.LineBasicMaterial({ color: colorMap['black'] });
            const lineGeometry = new THREE.BufferGeometry().setFromPoints([
                new THREE.Vector3((-250)*aspectWidth, 0, 0),
                new THREE.Vector3((-250)*aspectWidth, 0, yPosition*aspectDepth)
            ]);
            const line = new THREE.Line(lineGeometry, lineMaterial);
            scene.add(line);
            const arrowHelper = new THREE.ArrowHelper(
                new THREE.Vector3(0, 0, 1*aspectDepth), // Direction of the arrow
                new THREE.Vector3((-250)*aspectWidth, 0, yPosition*aspectDepth), // Start point
                10*aspectDepth, // Length of the arrow
                colorMap['black'], // Color of the arrow
                200*aspectDepth, // Head length
                100*aspectDepth // Head width
            );
            scene.add(arrowHelper);
        };

        // Function to add a text label at a given y position
        const addTextLabel = (yPos) => {
            yPosition = yPos; // Store original y position
            const loader = new FontLoader();
            loader.load('/static/node_modules/three/examples/fonts/optimer_bold.typeface.json', (font) => {
                const textGeometry = new TextGeometry(yPos.toString() + "mm", {
                    font: font,
                    size: 250,
                    depth: 5,
                    curveSegments: 12,
                    bevelEnabled: false
                });
                const textMaterial = new THREE.MeshBasicMaterial({ color: 0xFF0000 });
                textMesh = new THREE.Mesh(textGeometry, textMaterial); // Assign to global textMesh variable

                textGeometry.computeBoundingBox();
                textMesh.position.set((-1800)*aspectWidth, -400*aspectHeight, (yPos )*aspectDepth);
                scene.add(textMesh);
            });
        };

        // // Function to count boxes by row and color
        // const countBoxesByRowAndColor = (boxes) => {
        //     const rowCounts = {};
            

        //     boxes.forEach(box => {
        //         const row = box.row;
        //         const color = box.color;
        //         const boxHeight = box.dimensions.height;

        //         // Calculate the maximum number of boxes of this height that can fit in the row height
        //         const normalizedFactor = Math.floor(containerHeight / boxHeight);

        //         if (!rowCounts[row]) {
        //             rowCounts[row] = {};
        //         }

        //         if (!rowCounts[row][color]) {
        //             rowCounts[row][color] = 0;
        //         }

        //         // Increment the count by the normalized factor
        //         rowCounts[row][color] += (1 / normalizedFactor);
        //     });

        //     return rowCounts;
        // };

        // // Function to add count labels for each row
        // const addCountLabels = (rowCounts) => {
        //     const loader = new FontLoader();
        //     let labelOffsetZ = 0;

        //     // Load the font for the labels
        //     loader.load('/static/node_modules/three/examples/fonts/optimer_bold.typeface.json', (font) => {
        //         Object.keys(rowCounts).forEach(row => {
        //             const rowIndex = parseInt(row);
        //             const rowHeight = rowIndex * containerHeight / Object.keys(rowCounts).length; // Adjust label position by row index
        //             const rowData = rowCounts[row];
        //             // Initial offset for label placement along the z-axis

        //             let labelOffsetX = 0; // Offset for label placement along the x-axis

        //             Object.keys(rowData).forEach((color, index, array) => {
        //                 const count = Math.round(rowData[color]);
        //                 const labelText = `${count}`;
                        
        //                 // Create the text geometry and material for the count
        //                 const countGeometry = new TextGeometry(labelText, {
        //                     font: font,
        //                     size: 300,
        //                     depth: 10,
        //                     curveSegments: 12,
        //                     bevelEnabled: false
        //                 });

        //                 const countMaterial = new THREE.MeshBasicMaterial({ color: parseInt(color, 16) || 0xFFFFFF });

        //                 // Create the text mesh for the count
        //                 const countMesh = new THREE.Mesh(countGeometry, countMaterial);

        //                 // Compute the bounding box to center the text
        //                 countGeometry.computeBoundingBox();
        //                 const countBoundingBox = countGeometry.boundingBox;
        //                 const countWidth = countBoundingBox.max.x - countBoundingBox.min.x;

        //                 // Set the position of the count text
        //                 countMesh.position.set((containerWidth + 360 + labelOffsetX) * aspectWidth, 2500 * aspectHeight, (rowHeight + labelOffsetZ) * aspectDepth);

        //                 // Add the count text to the scene
        //                 scene.add(countMesh);

        //                 // Increment the offset for the next label along the x-axis
        //                 labelOffsetX += countWidth + 50; // Add distance between each label

        //                 // Check if the current item is not the last one to add a pipe
        //                 if (index < array.length - 1) {
        //                     // Create the text geometry and material for the pipe
        //                     const pipeGeometry = new TextGeometry('|', {
        //                         font: font,
        //                         size: 300,
        //                         depth: 10,
        //                         curveSegments: 12,
        //                         bevelEnabled: false
        //                     });

        //                     const pipeMaterial = new THREE.MeshBasicMaterial({ color: 0x000000 }); // Black color for the pipe

        //                     // Create the text mesh for the pipe
        //                     const pipeMesh = new THREE.Mesh(pipeGeometry, pipeMaterial);

        //                     // Compute the bounding box to center the pipe
        //                     pipeGeometry.computeBoundingBox();
        //                     const pipeBoundingBox = pipeGeometry.boundingBox;
        //                     const pipeWidth = pipeBoundingBox.max.x - pipeBoundingBox.min.x;

        //                     // Set the position of the pipe text
        //                     pipeMesh.position.set((containerWidth + 360 + labelOffsetX) * aspectWidth, 2500 * aspectHeight, (rowHeight + labelOffsetZ) * aspectDepth);

        //                     // Add the pipe text to the scene
        //                     scene.add(pipeMesh);

        //                     // Increment the offset for the next label along the x-axis
        //                     labelOffsetX += pipeWidth + 50; // Add distance after the pipe
        //                 }
        //             });
        //             labelOffsetZ += 250;
        //         });
        //         // labelOffsetZ += 250;
        //     });
        // };


        // Load coordinates from JSON file and create boxes
        fetch(threedPath)
            .then(response => response.json())
            .then(data => {
                const boxes = data.filter(item => item.start && item.end);
                const lastBoxYItem = data.find(item => item.last_box_y !== undefined);

                if (boxes.length > 0) {
                    createSmallBoxesFromCoordinates(boxes);

                    // Calculate box counts per row
                    // const rowCounts = countBoxesByRowAndColor(boxes);

                    // Add count labels to the scene
                    // addCountLabels(rowCounts);
                }

                if (lastBoxYItem) {
                    const lastBoxY = lastBoxYItem.last_box_y;
                    addVerticalLine(lastBoxY);
                    addHorizontalLine(lastBoxY);
                    addTextLabel(lastBoxY);
                }
            })
            .catch(error => console.error('Error loading coordinates:', error));

        // Add some light to the scene
        const ambientLight = new THREE.AmbientLight(0xffffff, 10);
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 2, 6000);
        directionalLight.position.set(5000, 8000, 5000);
        scene.add(directionalLight);

        const resetButton = document.getElementById('resetButton');
        const topViewButton = document.getElementById('topViewButton');
        const bottomViewButton = document.getElementById('bottomViewButton');
        const sideViewButton = document.getElementById('sideViewButton');

        // Function to reset the view
        const resetView = () => {
            camera.position.set(
                4.9 * containerWidth*aspectWidth, 4.9 * containerHeight*aspectHeight, 1.2* containerDepth*aspectDepth
            );
            orbit.target.set(
                containerWidth / 2 * aspectWidth,
                containerHeight / 2 * aspectHeight,
                containerDepth / 2 * aspectDepth
            );
            basePlate.visible = true;


            if (textMesh) {
                textMesh.position.set(
                    (containerWidth + 600) * aspectWidth,
                    -400*aspectHeight,
                    (yPosition + 100) * aspectDepth
                ); // Reset text position
                textMesh.rotation.set(0, 0, 0); // Reset text rotation
            }

            // Ensure the labels are facing the camera in the top view
            scene.traverse(object => {
                if (object.isMesh && object.geometry.type === 'TextGeometry') {
                    object.rotation.set(0, 0, 0); // Adjust label rotation for top view
                }
            });

            orbit.update();
        };

        // Function to set top view
        const setTopView = () => {
            camera.position.set(
                (containerWidth / 2) * aspectWidth,
                (containerHeight * 6) * aspectHeight,
                (containerDepth / 2) * aspectDepth
            );
            orbit.target.set(
                (containerWidth / 2) * aspectWidth,
                (containerHeight / 2) * aspectHeight,
                (containerDepth / 2) * aspectDepth
            );

            basePlate.visible = true;

            if (textMesh) {
                textMesh.rotation.x = -Math.PI / 2; // Rotate text by -90 degrees around X-axis
            }
            // Ensure the labels are facing the camera in the top view
            scene.traverse(object => {
                if (object.isMesh && object.geometry.type === 'TextGeometry') {
                    object.rotation.set(-Math.PI / 2, 0, 0); // Adjust label rotation for top view
                }
            });

            orbit.update();
        };

        // Function to set bottom view
        const setBottomView = () => {
            camera.position.set(
                (containerWidth / 2) * aspectWidth,
                (-6 * containerHeight) * aspectHeight,
                (containerDepth / 2) * aspectDepth
            );
            orbit.target.set(
                (containerWidth / 2) * aspectWidth,
                (containerHeight / 2) * aspectHeight,
                (containerDepth / 2) * aspectDepth
            );
            basePlate.visible = false;
            if (textMesh) {
                textMesh.rotation.x = Math.PI / 2; // Rotate text by 90 degrees around X-axis
            }

            scene.traverse(object => {
                if (object.isMesh && object.geometry.type === 'TextGeometry') {
                    object.rotation.set(Math.PI / 2, 0, 0); // Adjust label rotation for bottom view
                }
            });

            orbit.update();
        };

        // Function to set side view
        const setSideView = () => {
            camera.position.set(
                (containerWidth * 6) * aspectWidth,
                (containerHeight / 2) * aspectHeight,
                (containerDepth / 2) * aspectDepth
            );
            orbit.target.set(
                (containerWidth / 2) * aspectWidth,
                (containerHeight / 2) * aspectHeight,
                (containerDepth / 2) * aspectDepth
            );
            basePlate.visible = true;

            if (textMesh) {
                textMesh.rotation.set(0, Math.PI / 2, 
                0); // Rotate text by 90 degrees around Y-axis
                
            }

            scene.traverse(object => {
                if (object.isMesh && object.geometry.type === 'TextGeometry') {
                    object.rotation.set(0, Math.PI / 2, 0); // Adjust label rotation for side view
                }
            });

            orbit.update();
        };

        // Event listeners for buttons
        resetButton.addEventListener('click', resetView);
        topViewButton.addEventListener('click', setTopView);
        bottomViewButton.addEventListener('click', setBottomView);
        sideViewButton.addEventListener('click', setSideView);


        const gltfLoader = new GLTFLoader();
        gltfLoader.load('/static/3dmodels/group1.gltf', (gltf) => {
            const model = gltf.scene;

            // Scale the model to fit into the viewport
            model.scale.set(0.10, 0.10, 0.10);

            // Create an Object3D container for the model
            const modelContainer = new THREE.Object3D();
            modelContainer.add(model);
            // Create a secondary scene for the fixed model
            const fixedScene = new THREE.Scene();
            fixedScene.background = new THREE.Color('rgba(255, 255, 255, 1)');

            // Adjust the orthographic camera to the model

            // Set up lighting
            const directionalLight = new THREE.DirectionalLight(0xffffff, 3);
            directionalLight.position.set(1, 1, 1);
            directionalLight.castShadow = true;
            fixedScene.add(directionalLight);

            const ambientLight = new THREE.AmbientLight(0xffffff);
            fixedScene.add(ambientLight);

            // Enable shadows for the model
            model.traverse((node) => {
                if (node.isMesh) {
                    node.castShadow = true;
                    node.receiveShadow = true;
                }
            });

            // Configure the renderer to handle shadows
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;


            const fixedCamera = new THREE.OrthographicCamera(
                -1, 1, 1, 1, 0.1, 10000
            );
            fixedCamera.position.set(0, 0, 14); // Position the camera so it looks at the model
            fixedCamera.lookAt(0, 0, 0);

            // Position the model container in the fixed scene
            fixedScene.add(modelContainer);

            // Center the model based on its bounding box
            const box = new THREE.Box3().setFromObject(model);
            const center = box.getCenter(new THREE.Vector3());
            model.position.sub(center);  // Center the model at the origin

            // Animation loop
            // const addedPlates = [];


            // Initialize an array to store references to added plates
            const addedPlates = [];

            // Function to add a plate to the side based on the face
            function putPlateSide(face) {
                if (face.position.x !== 0) { // Check if the face is along the x-axis
                    // Define the geometry and material for the plate
                    const plate =  new THREE.BoxGeometry(containerHeight, containerDepth * aspectDepth, 50);
                    const makeBasePlate = new THREE.Mesh(plate, plateMaterialforSides);

                    // Rotate and position the plate based on the face
                    makeBasePlate.rotation.x = Math.PI / 2;
                    makeBasePlate.rotation.y = Math.PI / 2;
                    if (face.position.x > 0) {
                        makeBasePlate.position.set(1 * containerWidth+25, containerHeight / 2, containerDepth);
                    } else {
                        makeBasePlate.position.set(-25, containerHeight / 2, containerDepth); 
                    }


                    // Add the plate to the scene
                    scene.add(makeBasePlate);

                    // Store a reference to the plate and its corresponding face's normal in the array
                    addedPlates.push({ plate: makeBasePlate, normal: face.normal.clone() });
                }
            }

            // Function to remove the plate from the side based on the face
            function removePlateSide(face) {
                // Iterate through the addedPlates array to find the plate with the same normal as the face
                for (let i = 0; i < addedPlates.length; i++) {
                    const plateEntry = addedPlates[i];

                    // Check if the normal matches
                    if (plateEntry.normal.equals(face.normal)) {
                        // Remove the plate from the scene
                        scene.remove(plateEntry.plate);

                        // Dispose of the geometry and material to free up resources
                        plateEntry.plate.geometry.dispose();
                        plateEntry.plate.material.dispose();

                        // Remove the entry from the array
                        addedPlates.splice(i, 1);
                    }
                }
            }


            function animate() {
                requestAnimationFrame(animate);

                // Update camera controls
                orbit.update();

                // Render the main scene
                renderer.setViewport(0, 0, window.innerWidth, window.innerHeight);
                renderer.setScissor(0, 0, window.innerWidth, window.innerHeight);
                renderer.setScissorTest(true);
                renderer.clear();
                renderer.render(scene, camera);

                // Set the viewport for the fixed scene rendering (top-right corner)
                const viewportWidth = window.innerWidth / 6;  // 1/4 of the width
                const viewportHeight = window.innerHeight / 4;  // 1/4 of the height
                renderer.setViewport(window.innerWidth - viewportWidth-window.innerWidth/20, window.innerHeight - viewportHeight-window.innerHeight/20, viewportWidth, viewportHeight);
                renderer.setScissor(window.innerWidth - viewportWidth-window.innerWidth/20, window.innerHeight - viewportHeight-window.innerHeight/20, viewportWidth, viewportHeight);
                renderer.setScissorTest(true);

                // Ensure the fixed model container follows the main camera's rotation
                modelContainer.quaternion.copy(camera.quaternion.clone().invert());

                // Adjust the fixed camera to fit the viewport
                fixedCamera.left = -viewportWidth / 2 / 10;  // Adjust based on model scale
                fixedCamera.right = viewportWidth / 2 / 10;
                fixedCamera.top = viewportHeight / 2 / 10;
                fixedCamera.bottom = -viewportHeight / 2 / 10;
                fixedCamera.updateProjectionMatrix();
                

                // Render the fixed scene in the small viewport
                renderer.clearDepth();  // Clear depth buffer so fixedScene renders on top
                renderer.render(fixedScene, fixedCamera);

                // Iterate over faces and apply the visibility logic
                faces.forEach(face => {
                    // Compute the vector from the camera to a point on the face
                    const vectorToFace = new THREE.Vector3().subVectors(face.position, camera.position);

                    // Calculate the dot product
                    const dotProduct = vectorToFace.dot(face.normal);

                    // Determine visibility based on the sign of the dot product
                    if (dotProduct > 0) {
                        putPlateSide(face);
                    }else{
                        removePlateSide(face);
                    }
                });

            }

            animate();
        });

        // Adjust the camera and renderer on window resize
        window.addEventListener('resize', () => {
            const aspect = window.innerWidth / window.innerHeight;
            camera.aspect = aspect;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    });









    
});
// const renderer = new THREE.WebGLRenderer({ antialias: true });
// renderer.setPixelRatio(window.devicePixelRatio);
// renderer.setSize(window.innerWidth, window.innerHeight);
// document.body.appendChild(renderer.domElement);

// // Scene setup
// const scene = new THREE.Scene();
// scene.background = new THREE.Color(0xffffff);

// // Camera setup
// const camera = new THREE.PerspectiveCamera(
//     70,
//     window.innerWidth / window.innerHeight,
//     0.1,
//     500000
// );
// const orbit = new OrbitControls(camera, renderer.domElement);

// // For making restrictions to the rotation of the camera like they have done in Easy Cargo.
// // orbit.enablePan = false; // Disable panning for simplicity
// // orbit.minPolarAngle = Math.PI / 8; // Minimum polar angle (from top view)
// // orbit.maxPolarAngle = Math.PI / 2.1; // Maximum polar angle (from top view)
// // orbit.minAzimuthAngle = -Infinity; // Minimum azimuth angle
// // orbit.maxAzimuthAngle = Infinity; // Maximum azimuth angle
// // orbit.update();

// const textureLoader = new THREE.TextureLoader();
// const rustyTexture = textureLoader.load('/static/images/rust3.png', function (texture) {
//     // Adjust texture wrapping and repeat as needed
//     texture.wrapS = THREE.RepeatWrapping;
//     texture.wrapT = THREE.RepeatWrapping;
//     texture.repeat.set(1, 1); // Adjust these values to control how the texture is repeated
// });

// let containerWidth;
// let containerHeight;
// let containerDepth;

// // Function to initialize container dimensions
// function fetchContainerDimensions() {
//     return fetch('/static/files/container_info_0.json')
//         .then(response => {
//             if (!response.ok) {
//                 throw new Error('Network response was not ok');
//             }
//             return response.json();
//         })
//         .then(containerInfo => {
//             containerWidth = containerInfo.containerWidth;
//             containerHeight = containerInfo.containerHeight;
//             containerDepth = containerInfo.containerLength; // Ensure this field name matches your JSON

//             console.log('Container Width (inside fetch):', containerWidth);
//             console.log('Container Height (inside fetch):', containerHeight);
//             console.log('Container Depth (inside fetch):', containerDepth);

//             // Return an object with the dimensions
//             return { containerWidth, containerHeight, containerDepth };
//         })
//         .catch(error => console.error('Error loading container info:', error));
// }

// // Call the function and use the dimensions once fetched


// const aspectWidth = 1; // This is the base aspect (1x)
// const aspectHeight = 1; // Height relative to width
// const aspectDepth = 2;

// fetchContainerDimensions().then(dimensions => {
   

//     // Your further logic here, using the dimensions
//     const faces = [
//         { normal: new THREE.Vector3(1, 0, 0), position: new THREE.Vector3(containerWidth, 0, 0) },    // Right face
//         { normal: new THREE.Vector3(-1, 0, 0), position: new THREE.Vector3(-containerWidth, 0, 0) }, // Left face
//         { normal: new THREE.Vector3(0, 1, 0), position: new THREE.Vector3(0, containerHeight, 0) },  // Top face
//         // { normal: new THREE.Vector3(0, -1, 0), position: new THREE.Vector3(0, -containerHeight, 0) }, // Bottom face
//         { normal: new THREE.Vector3(0, 0, 1), position: new THREE.Vector3(0, 0, containerDepth) },    // Front face
//         { normal: new THREE.Vector3(0, 0, -1), position: new THREE.Vector3(0, 0, -containerDepth) }   // Back face
//     ];

//         // Set the target of the OrbitControls to the center of the container
//     orbit.target.set((containerWidth / 2)*aspectWidth, (containerHeight / 2)*aspectHeight, (containerDepth / 2)*aspectDepth);
//     orbit.update();

//     camera.position.set(3.5 * containerWidth*aspectWidth, 3 * containerHeight*aspectHeight, 1.4* containerDepth*aspectDepth);
//     orbit.update();

//     // Axes helper
//     const axesHelper = new THREE.AxesHelper(1000);
//     scene.add(axesHelper);

//     // Container wireframe
//     const containerGeometry = new THREE.BoxGeometry(containerWidth, containerHeight, containerDepth);
//     const containerEdges = new THREE.EdgesGeometry(containerGeometry);
//     const containerMaterial = new THREE.LineBasicMaterial({ color: 0x000, transparent: true, opacity: 0.5 });
//     const containerWireframe = new THREE.LineSegments(containerEdges, containerMaterial);

//     const plateGeometry = new THREE.BoxGeometry(containerWidth, containerDepth*aspectDepth,200);
//     const plateMaterial = new THREE.MeshStandardMaterial({
//         // map:rustyTexture, 
//         side: THREE.DoubleSide,
//         // metalness:0.9,
//         color:0xd3d3d3d

//     });

//     const plateMaterialforSides = new THREE.MeshStandardMaterial({
//         map:rustyTexture, 
//         side: THREE.DoubleSide,
//         metalness:0.9,
//         opacity:1,
//         color:0xB87333

//     });

//     const basePlate = new THREE.Mesh(plateGeometry, plateMaterial);

//     // Position the base plate at the bottom of the container
//     basePlate.rotation.x = Math.PI / 2; // Rotate to make it horizontal
//     basePlate.position.set(
//         (containerWidth / 2) ,
//         -100, // Bottom of the container
//         (containerDepth / 2)*aspectDepth 
//     );

//     scene.add(basePlate);

//     // Calculate aspect ratios relative to the container width
//     // Depth relative to width

//     const plate = new THREE.BoxGeometry(containerWidth, containerHeight * aspectHeight, 100);
//     const makeBasePlate = new THREE.Mesh(plate,plateMaterialforSides);
//     makeBasePlate.position.set(containerWidth/2,containerHeight/2,-50);
//     scene.add(makeBasePlate);


//     // Apply scaling to the container wireframe to maintain the aspect ratio
//     containerWireframe.scale.set(aspectWidth, aspectHeight, aspectDepth);
//     containerWireframe.position.set(
//         (containerWidth / 2) * aspectWidth,
//         (containerHeight / 2) * aspectHeight,
//         (containerDepth / 2) * aspectDepth
//     );

//     scene.add(containerWireframe);

    
//     // Color mapping from names to hex codes
//     const colorMap = {
//         "red": 0xFF0000,
//         "green": 0x00FF00,
//         "blue": 0x0000FF,
//         "yellow": 0xFFFF00,
//         "purple": 0x800080,
//         "orange": 0xFFA500,
//         "black": 0x000000,
//     };

//     let textMesh; // Declare textMesh globally
//     let yPosition; // Store original y position

//     // Function to create and place small boxes using coordinates from JSON
//     const createSmallBoxesFromCoordinates = (boxes) => {
//         boxes.forEach(box => {
//             const startX = box.start.x;
//             const startZ = containerDepth - box.start.y;
//             const startY = box.start.z;

//             const endX = box.end.x;
//             const endY = box.end.z;
//             const endZ = containerDepth - box.end.y;
//             const colorName = box.color;

//             const smallBoxWidth = box.dimensions.width;
//             const smallBoxHeight = box.dimensions.height;
//             const smallBoxDepth = box.dimensions.length;

//             const centerX = startX + smallBoxWidth / 2;
//             const centerY = startY + smallBoxHeight / 2;
//             const centerZ = startZ - smallBoxDepth / 2;

//             const smallBoxGeometry = new THREE.BoxGeometry(smallBoxWidth, smallBoxHeight, smallBoxDepth);
//             const smallBoxMaterial = new THREE.MeshStandardMaterial({
//                 color: colorMap[colorName] || 0xFFFFFF,
//                 transparent: true,
//                 opacity: 0.9,
//                 side: THREE.DoubleSide
//             });
//             const smallBox = new THREE.Mesh(smallBoxGeometry, smallBoxMaterial);

//             // Apply the same aspect ratio scaling to the small boxes
//             smallBox.scale.set(aspectWidth, aspectHeight, aspectDepth);

//             // Adjust position to account for scaling
//             smallBox.position.set(
//                 centerX * aspectWidth,
//                 centerY * aspectHeight,
//                 centerZ * aspectDepth
//             );

//             scene.add(smallBox);

//             const smallBoxEdges = new THREE.EdgesGeometry(smallBoxGeometry);
//             const smallBoxEdgesMaterial = new THREE.LineBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.5 });
//             const smallBoxWireframe = new THREE.LineSegments(smallBoxEdges, smallBoxEdgesMaterial);
//             // smallBox.scale.set(aspectWidth, aspectHeight, aspectDepth);
//             smallBoxWireframe.scale.set(aspectWidth, aspectHeight, aspectDepth);


//             // Adjust position to account for scaling
//             smallBoxWireframe.position.set(
//                 centerX * aspectWidth,
//                 centerY * aspectHeight,
//                 centerZ * aspectDepth
//             );

//             scene.add(smallBoxWireframe);
//         });
//     };

//     // Function to add a horizontal line at a given y position
//     const addHorizontalLine = (yPosition) => {
//         const lineMaterial = new THREE.LineBasicMaterial({ color: 0xFF0000 });
//         const lineGeometry = new THREE.BufferGeometry().setFromPoints([
//             new THREE.Vector3(0*aspectWidth, 0*aspectHeight, yPosition*aspectDepth),
//             new THREE.Vector3(containerWidth*aspectWidth, 0*aspectHeight, yPosition*aspectDepth)
//         ]);
//         const line = new THREE.Line(lineGeometry, lineMaterial);
//         scene.add(line);
//     };

//     const addVerticalLine = (yPosition) => {
//         const lineMaterial = new THREE.LineBasicMaterial({ color: colorMap['black'] });
//         const lineGeometry = new THREE.BufferGeometry().setFromPoints([
//             new THREE.Vector3((-250)*aspectWidth, 0, 0),
//             new THREE.Vector3((-250)*aspectWidth, 0, yPosition*aspectDepth)
//         ]);
//         const line = new THREE.Line(lineGeometry, lineMaterial);
//         scene.add(line);
//         const arrowHelper = new THREE.ArrowHelper(
//             new THREE.Vector3(0, 0, 1*aspectDepth), // Direction of the arrow
//             new THREE.Vector3((-250)*aspectWidth, 0, yPosition*aspectDepth), // Start point
//             10*aspectDepth, // Length of the arrow
//             colorMap['black'], // Color of the arrow
//             200*aspectDepth, // Head length
//             100*aspectDepth // Head width
//         );
//         scene.add(arrowHelper);
//     };

//     // Function to add a text label at a given y position
//     const addTextLabel = (yPos) => {
//         yPosition = yPos; // Store original y position
//         const loader = new FontLoader();
//         loader.load('/static/node_modules/three/examples/fonts/optimer_bold.typeface.json', (font) => {
//             const textGeometry = new TextGeometry(yPos.toString() + "mm", {
//                 font: font,
//                 size: 250,
//                 depth: 5,
//                 curveSegments: 12,
//                 bevelEnabled: false
//             });
//             const textMaterial = new THREE.MeshBasicMaterial({ color: 0xFF0000 });
//             textMesh = new THREE.Mesh(textGeometry, textMaterial); // Assign to global textMesh variable

//             textGeometry.computeBoundingBox();
//             textMesh.position.set((-1800)*aspectWidth, -400*aspectHeight, (yPos )*aspectDepth);
//             scene.add(textMesh);
//         });
//     };

//     // Function to count boxes by row and color
//     const countBoxesByRowAndColor = (boxes) => {
//         const rowCounts = {};
        

//         boxes.forEach(box => {
//             const row = box.row;
//             const color = box.color;
//             const boxHeight = box.dimensions.height;

//             // Calculate the maximum number of boxes of this height that can fit in the row height
//             const normalizedFactor = Math.floor(containerHeight / boxHeight);

//             if (!rowCounts[row]) {
//                 rowCounts[row] = {};
//             }

//             if (!rowCounts[row][color]) {
//                 rowCounts[row][color] = 0;
//             }

//             // Increment the count by the normalized factor
//             rowCounts[row][color] += (1 / normalizedFactor);
//         });

//         return rowCounts;
//     };

//     // Function to add count labels for each row
//     const addCountLabels = (rowCounts) => {
//         const loader = new FontLoader();
//         let labelOffsetZ = 0;

//         // Load the font for the labels
//         loader.load('/static/node_modules/three/examples/fonts/optimer_bold.typeface.json', (font) => {
//             Object.keys(rowCounts).forEach(row => {
//                 const rowIndex = parseInt(row);
//                 const rowHeight = rowIndex * containerHeight / Object.keys(rowCounts).length; // Adjust label position by row index
//                 const rowData = rowCounts[row];
//                 // Initial offset for label placement along the z-axis

//                 let labelOffsetX = 0; // Offset for label placement along the x-axis

//                 Object.keys(rowData).forEach((color, index, array) => {
//                     const count = Math.round(rowData[color]);
//                     const labelText = `${count}`;
                    
//                     // Create the text geometry and material for the count
//                     const countGeometry = new TextGeometry(labelText, {
//                         font: font,
//                         size: 300,
//                         depth: 10,
//                         curveSegments: 12,
//                         bevelEnabled: false
//                     });

//                     const countMaterial = new THREE.MeshBasicMaterial({ color: colorMap[color] || 0xFFFFFF });

//                     // Create the text mesh for the count
//                     const countMesh = new THREE.Mesh(countGeometry, countMaterial);

//                     // Compute the bounding box to center the text
//                     countGeometry.computeBoundingBox();
//                     const countBoundingBox = countGeometry.boundingBox;
//                     const countWidth = countBoundingBox.max.x - countBoundingBox.min.x;

//                     // Set the position of the count text
//                     countMesh.position.set((containerWidth + 360 + labelOffsetX) * aspectWidth, 2500 * aspectHeight, (rowHeight + labelOffsetZ) * aspectDepth);

//                     // Add the count text to the scene
//                     scene.add(countMesh);

//                     // Increment the offset for the next label along the x-axis
//                     labelOffsetX += countWidth + 50; // Add distance between each label

//                     // Check if the current item is not the last one to add a pipe
//                     if (index < array.length - 1) {
//                         // Create the text geometry and material for the pipe
//                         const pipeGeometry = new TextGeometry('|', {
//                             font: font,
//                             size: 300,
//                             depth: 10,
//                             curveSegments: 12,
//                             bevelEnabled: false
//                         });

//                         const pipeMaterial = new THREE.MeshBasicMaterial({ color: 0x000000 }); // Black color for the pipe

//                         // Create the text mesh for the pipe
//                         const pipeMesh = new THREE.Mesh(pipeGeometry, pipeMaterial);

//                         // Compute the bounding box to center the pipe
//                         pipeGeometry.computeBoundingBox();
//                         const pipeBoundingBox = pipeGeometry.boundingBox;
//                         const pipeWidth = pipeBoundingBox.max.x - pipeBoundingBox.min.x;

//                         // Set the position of the pipe text
//                         pipeMesh.position.set((containerWidth + 360 + labelOffsetX) * aspectWidth, 2500 * aspectHeight, (rowHeight + labelOffsetZ) * aspectDepth);

//                         // Add the pipe text to the scene
//                         scene.add(pipeMesh);

//                         // Increment the offset for the next label along the x-axis
//                         labelOffsetX += pipeWidth + 50; // Add distance after the pipe
//                     }
//                 });
//                 labelOffsetZ += 250;
//             });
//             // labelOffsetZ += 250;
//         });
//     };


//     // Load coordinates from JSON file and create boxes
//     fetch('/static/files/box_coordinates_0.json')
//         .then(response => response.json())
//         .then(data => {
//             const boxes = data.filter(item => item.start && item.end);
//             const lastBoxYItem = data.find(item => item.last_box_y !== undefined);

//             if (boxes.length > 0) {
//                 createSmallBoxesFromCoordinates(boxes);

//                 // Calculate box counts per row
//                 const rowCounts = countBoxesByRowAndColor(boxes);

//                 // Add count labels to the scene
//                 addCountLabels(rowCounts);
//             }

//             if (lastBoxYItem) {
//                 const lastBoxY = lastBoxYItem.last_box_y;
//                 addVerticalLine(lastBoxY);
//                 addHorizontalLine(lastBoxY);
//                 addTextLabel(lastBoxY);
//             }
//         })
//         .catch(error => console.error('Error loading coordinates:', error));

//     // Add some light to the scene
//     const ambientLight = new THREE.AmbientLight(0xffffff, 10);
//     scene.add(ambientLight);

//     const directionalLight = new THREE.DirectionalLight(0xffffff, 2, 6000);
//     directionalLight.position.set(5000, 8000, 5000);
//     scene.add(directionalLight);

//     const resetButton = document.getElementById('resetButton');
//     const topViewButton = document.getElementById('topViewButton');
//     const bottomViewButton = document.getElementById('bottomViewButton');
//     const sideViewButton = document.getElementById('sideViewButton');

//     // Function to reset the view
//     const resetView = () => {
//         camera.position.set(
//             3.5 * containerWidth * aspectWidth,
//             3 * containerHeight * aspectHeight,
//             1.4* containerDepth * aspectDepth
//         );
//         orbit.target.set(
//             containerWidth / 2 * aspectWidth,
//             containerHeight / 2 * aspectHeight,
//             containerDepth / 2 * aspectDepth
//         );
//         basePlate.visible = true;


//         if (textMesh) {
//             textMesh.position.set(
//                 (containerWidth + 600) * aspectWidth,
//                 -400*aspectHeight,
//                 (yPosition + 100) * aspectDepth
//             ); // Reset text position
//             textMesh.rotation.set(0, 0, 0); // Reset text rotation
//         }

//         // Ensure the labels are facing the camera in the top view
//         scene.traverse(object => {
//             if (object.isMesh && object.geometry.type === 'TextGeometry') {
//                 object.rotation.set(0, 0, 0); // Adjust label rotation for top view
//             }
//         });

//         orbit.update();
//     };

//     // Function to set top view
//     const setTopView = () => {
//         camera.position.set(
//             (containerWidth / 2) * aspectWidth,
//             (containerHeight * 6) * aspectHeight,
//             (containerDepth / 2) * aspectDepth
//         );
//         orbit.target.set(
//             (containerWidth / 2) * aspectWidth,
//             (containerHeight / 2) * aspectHeight,
//             (containerDepth / 2) * aspectDepth
//         );

//         basePlate.visible = true;

//         if (textMesh) {
//             textMesh.rotation.x = -Math.PI / 2; // Rotate text by -90 degrees around X-axis
//         }
//         // Ensure the labels are facing the camera in the top view
//         scene.traverse(object => {
//             if (object.isMesh && object.geometry.type === 'TextGeometry') {
//                 object.rotation.set(-Math.PI / 2, 0, 0); // Adjust label rotation for top view
//             }
//         });

//         orbit.update();
//     };

//     // Function to set bottom view
//     const setBottomView = () => {
//         camera.position.set(
//             (containerWidth / 2) * aspectWidth,
//             (-6 * containerHeight) * aspectHeight,
//             (containerDepth / 2) * aspectDepth
//         );
//         orbit.target.set(
//             (containerWidth / 2) * aspectWidth,
//             (containerHeight / 2) * aspectHeight,
//             (containerDepth / 2) * aspectDepth
//         );
//         basePlate.visible = false;
//         if (textMesh) {
//             textMesh.rotation.x = Math.PI / 2; // Rotate text by 90 degrees around X-axis
//         }

//         scene.traverse(object => {
//             if (object.isMesh && object.geometry.type === 'TextGeometry') {
//                 object.rotation.set(Math.PI / 2, 0, 0); // Adjust label rotation for bottom view
//             }
//         });

//         orbit.update();
//     };

//     // Function to set side view
//     const setSideView = () => {
//         camera.position.set(
//             (containerWidth * 6) * aspectWidth,
//             (containerHeight / 2) * aspectHeight,
//             (containerDepth / 2) * aspectDepth
//         );
//         orbit.target.set(
//             (containerWidth / 2) * aspectWidth,
//             (containerHeight / 2) * aspectHeight,
//             (containerDepth / 2) * aspectDepth
//         );
//         basePlate.visible = true;

//         if (textMesh) {
//             textMesh.rotation.set(0, Math.PI / 2, 
//             0); // Rotate text by 90 degrees around Y-axis
            
//         }

//         scene.traverse(object => {
//             if (object.isMesh && object.geometry.type === 'TextGeometry') {
//                 object.rotation.set(0, Math.PI / 2, 0); // Adjust label rotation for side view
//             }
//         });

//         orbit.update();
//     };

//     // Event listeners for buttons
//     resetButton.addEventListener('click', resetView);
//     topViewButton.addEventListener('click', setTopView);
//     bottomViewButton.addEventListener('click', setBottomView);
//     sideViewButton.addEventListener('click', setSideView);


//     const gltfLoader = new GLTFLoader();
//     gltfLoader.load('/static/3dmodels/group1.gltf', (gltf) => {
//         const model = gltf.scene;

//         // Scale the model to fit into the viewport
//         model.scale.set(0.10, 0.10, 0.10);

//         // Create an Object3D container for the model
//         const modelContainer = new THREE.Object3D();
//         modelContainer.add(model);
//         // Create a secondary scene for the fixed model
//         const fixedScene = new THREE.Scene();
//         fixedScene.background = new THREE.Color(0xffffff);

//         // Adjust the orthographic camera to the model

//         // Set up lighting
//         const directionalLight = new THREE.DirectionalLight(0xffffff, 3);
//         directionalLight.position.set(1, 1, 1);
//         directionalLight.castShadow = true;
//         fixedScene.add(directionalLight);

//         const ambientLight = new THREE.AmbientLight(0xffffff);
//         fixedScene.add(ambientLight);

//         // Enable shadows for the model
//         model.traverse((node) => {
//             if (node.isMesh) {
//                 node.castShadow = true;
//                 node.receiveShadow = true;
//             }
//         });

//         // Configure the renderer to handle shadows
//         renderer.shadowMap.enabled = true;
//         renderer.shadowMap.type = THREE.PCFSoftShadowMap;


//         const fixedCamera = new THREE.OrthographicCamera(
//             -1, 1, 1, 1, 0.1, 10000
//         );
//         fixedCamera.position.set(0, 0, 14); // Position the camera so it looks at the model
//         fixedCamera.lookAt(0, 0, 0);

//         // Position the model container in the fixed scene
//         fixedScene.add(modelContainer);

//         // Center the model based on its bounding box
//         const box = new THREE.Box3().setFromObject(model);
//         const center = box.getCenter(new THREE.Vector3());
//         model.position.sub(center);  // Center the model at the origin

//         // Animation loop
//         // const addedPlates = [];


//         // Initialize an array to store references to added plates
//         const addedPlates = [];

//         // Function to add a plate to the side based on the face
//         function putPlateSide(face) {
//             if (face.position.x !== 0) { // Check if the face is along the x-axis
//                 // Define the geometry and material for the plate
//                 const plate =  new THREE.BoxGeometry(containerHeight, containerDepth * aspectDepth, 50);
//                 const makeBasePlate = new THREE.Mesh(plate, plateMaterialforSides);

//                 // Rotate and position the plate based on the face
//                 makeBasePlate.rotation.x = Math.PI / 2;
//                 makeBasePlate.rotation.y = Math.PI / 2;
//                 if (face.position.x > 0) {
//                     makeBasePlate.position.set(1 * containerWidth+25, containerHeight / 2, containerDepth);
//                 } else {
//                     makeBasePlate.position.set(-25, containerHeight / 2, containerDepth); 
//                 }


//                 // Add the plate to the scene
//                 scene.add(makeBasePlate);

//                 // Store a reference to the plate and its corresponding face's normal in the array
//                 addedPlates.push({ plate: makeBasePlate, normal: face.normal.clone() });
//             }
//         }

//         // Function to remove the plate from the side based on the face
//         function removePlateSide(face) {
//             // Iterate through the addedPlates array to find the plate with the same normal as the face
//             for (let i = 0; i < addedPlates.length; i++) {
//                 const plateEntry = addedPlates[i];

//                 // Check if the normal matches
//                 if (plateEntry.normal.equals(face.normal)) {
//                     // Remove the plate from the scene
//                     scene.remove(plateEntry.plate);

//                     // Dispose of the geometry and material to free up resources
//                     plateEntry.plate.geometry.dispose();
//                     plateEntry.plate.material.dispose();

//                     // Remove the entry from the array
//                     addedPlates.splice(i, 1);
//                 }
//             }
//         }


//         function animate() {
//             requestAnimationFrame(animate);

//             // Update camera controls
//             orbit.update();

//             // Render the main scene
//             renderer.setViewport(0, 0, window.innerWidth, window.innerHeight);
//             renderer.setScissor(0, 0, window.innerWidth, window.innerHeight);
//             renderer.setScissorTest(true);
//             renderer.clear();
//             renderer.render(scene, camera);

//             // Set the viewport for the fixed scene rendering (top-right corner)
//             const viewportWidth = window.innerWidth / 6;  // 1/4 of the width
//             const viewportHeight = window.innerHeight / 4;  // 1/4 of the height
//             renderer.setViewport(window.innerWidth - viewportWidth-window.innerWidth/20, window.innerHeight - viewportHeight-window.innerHeight/20, viewportWidth, viewportHeight);
//             renderer.setScissor(window.innerWidth - viewportWidth-window.innerWidth/20, window.innerHeight - viewportHeight-window.innerHeight/20, viewportWidth, viewportHeight);
//             renderer.setScissorTest(true);

//             // Ensure the fixed model container follows the main camera's rotation
//             modelContainer.quaternion.copy(camera.quaternion.clone().invert());

//             // Adjust the fixed camera to fit the viewport
//             fixedCamera.left = -viewportWidth / 2 / 10;  // Adjust based on model scale
//             fixedCamera.right = viewportWidth / 2 / 10;
//             fixedCamera.top = viewportHeight / 2 / 10;
//             fixedCamera.bottom = -viewportHeight / 2 / 10;
//             fixedCamera.updateProjectionMatrix();
            

//             // Render the fixed scene in the small viewport
//             renderer.clearDepth();  // Clear depth buffer so fixedScene renders on top
//             renderer.render(fixedScene, fixedCamera);

//             // Iterate over faces and apply the visibility logic
//             faces.forEach(face => {
//                 // Compute the vector from the camera to a point on the face
//                 const vectorToFace = new THREE.Vector3().subVectors(face.position, camera.position);

//                 // Calculate the dot product
//                 const dotProduct = vectorToFace.dot(face.normal);

//                 // Determine visibility based on the sign of the dot product
//                 if (dotProduct > 0) {
//                     putPlateSide(face);
//                 }else{
//                     removePlateSide(face);
//                 }
//             });

//         }

//         animate();
//     });

//     // Adjust the camera and renderer on window resize
//     window.addEventListener('resize', () => {
//         const aspect = window.innerWidth / window.innerHeight;
//         camera.aspect = aspect;
//         camera.updateProjectionMatrix();
//         renderer.setSize(window.innerWidth, window.innerHeight);
//     });
// });








