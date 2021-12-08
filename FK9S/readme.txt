####
release notes:
Beta0.1:    fulfill basic checking about k8s basic components(namespace, pod, service, etc.. Check function logic for all elements supported).
Beta0.2:    support pod log/basic info checking.
            support abnormal status content list
            support get yaml config or description for supported element
Beta0.3:    now configmap used by pod will be displayed in pod basic info page
            Support periodically page refresh for level2 state page. Refresh interval 2s. Press F to active/deactive auto refresh
[Plan for Beta0.4]:
            add searching function page
            add paging capabilities

####
Pre-condition:
(example for SecureCRT, other terminal tool can change the setting accordingly)
Under: Session Options -- Terminal -- Emulation
Terminal should choose Linux or Xterm
make sure Logical columns more than 150

####
Usage:
1. At any path of director:
> vi fk9s.py
2. Copy the content to the file
3. run the tool
> python3 fk9s.py
