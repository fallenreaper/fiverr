<form id="jobsiteform" action="insert.php" method="POST">

    <h1>Add a Jobsite:</h1>
    
    <!-- One "tab" for each step in the form: -->
    <div class="tab">Job Description:
      <p><input type="text" name="jobname" placeholder="Job Name..." oninput="this.className = ''"></p>
      <p><input type="text" name="jobaddress" placeholder="Job Address..." oninput="this.className = ''"></p>
      <p><input type="text" name="joblead" placeholder="Job Lead..." oninput="this.className = ''"></p>
      <p><input type="text" name="jobstart" placeholder="Est. Job Start..." oninput="this.className = ''"></p>
      <p><input type="text" name="jobend" placeholder="Est. Job End..." oninput="this.className = ''"></p>
      <p><input type="text" name="estimatedhours" placeholder="Est. Hours..." oninput="this.className = ''"></p>
    </div>

    <div class="tab">Equipment Info:
        <p><select id="Grinder/Screener" name="screener" autofocus>
            <option value="bigpete1">5710D #1</option>
            <option value="bigpete2">5710D #2</option>
            <option value="lilpete">2700B</option>
            <option value="screener">Screener</option>
        </select></p>
        <p><select id="Excavator" name="excavator" autofocus>
            <option value="pc2901">PC290-1</option>
            <option value="pc2902">PC290-2</option>
            <option value="noexcavator">No Excavator</option>
        </select></p>
        <p><select id="Shear" name="shear" autofocus>
            <option value="pc210">PC210</option>
            <option value="pc240">PC240</option>
            <option value="noshear">No Shear</option>
        </select></p>
        <p><select id="Wheel Loader" name="loader" autofocus>
            <option value="wa270grapple">WA-270 Grapple</option>
            <option value="wa270bucket">WA-270 Bucket</option>
            <option value="noloader">No Loader</option>
        </select></p>
    </div>
    
    <div class="tab">Hauling Info:
        <p><input type="text" name="haulingcompany" placeholder="Hauling Company..." oninput="this.className = ''"></p>
        <p><input type="text" name="estimatedloads" placeholder="Est. Loads..." oninput="this.className = ''"></p>
        <p><input type="text" name="loaddestination" placeholder="Where are the loads going?.." oninput="this.className = ''"></p>
        <p><input type="text" name="haulingnotes" placeholder="Hauling notes:..." oninput="this.className = ''"></p>
    </div>
    
    <div class="tab">Fuel Info:
        <p><input type="text" name="fuelprovider" placeholder="Fuel Provider Name..." oninput="this.className = ''"></p>
        <p><input type="text" name="fuelphonenumber" placeholder="Fuel Provider Phone Number..." oninput="this.className = ''"></p>
        <p><input type="text" name="fuelnotes" placeholder="Other Fuel Notes..." oninput="this.className = ''"></p>
    </div>
    
    <div class="tab">Crew & Area Info:
        <p><input type="text" name="crewlodging" placeholder="Crew Lodging Situation..." oninput="this.className = ''"></p>
        <p><input type="text" name="crewnotes" placeholder="NOTES: Site conditions.., safety hazards.., etc.." oninput="this.className = ''"></p>
    </div>
    
    <div style="overflow:auto;">
      <div style="float:right;">
        <button type="button" id="prevBtn" onclick="nextPrev(-1)">Previous</button>
        <button type="button" id="nextBtn" onclick="nextPrev(1)">Next</button>
      </div>
    </div>
    
    <!-- Circles which indicates the steps of the form: -->
    <div style="text-align:center;margin-top:40px;">
      <span class="step"></span>
      <span class="step"></span>
      <span class="step"></span>
      <span class="step"></span>
    </div>
    
    <input type="submit" name="submit" value="Submit">

    </form>