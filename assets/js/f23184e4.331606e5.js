(self.webpackChunkdocs_website=self.webpackChunkdocs_website||[]).push([[249],{9475:function(e,t,r){"use strict";r.r(t),r.d(t,{frontMatter:function(){return c},contentTitle:function(){return i},metadata:function(){return d},toc:function(){return l},default:function(){return u}});var o=r(2122),n=r(9756),s=(r(7294),r(3905)),a=["components"],c={sidebar_position:3,sidebar_label:"Adding Custom Matchers",title:"Adding Custom Matchers"},i=void 0,d={unversionedId:"workflows/custom_matchers",id:"workflows/custom_matchers",isDocsHomePage:!1,title:"Adding Custom Matchers",description:"In some cases you'd want to add custom request macthers to Cornell.",source:"@site/docs/workflows/custom_matchers.md",sourceDirName:"workflows",slug:"/workflows/custom_matchers",permalink:"/cornell/docs/workflows/custom_matchers",version:"current",sidebarPosition:3,frontMatter:{sidebar_position:3,sidebar_label:"Adding Custom Matchers",title:"Adding Custom Matchers"},sidebar:"defaultSidebar",previous:{title:"Starting Cornell from your own module",permalink:"/cornell/docs/workflows/own_module"},next:{title:"Subscribing to Hooks",permalink:"/cornell/docs/workflows/subscribing_to_hooks"}},l=[],m={toc:l};function u(e){var t=e.components,r=(0,n.Z)(e,a);return(0,s.kt)("wrapper",(0,o.Z)({},m,r,{components:t,mdxType:"MDXLayout"}),(0,s.kt)("p",null,"In some cases you'd want to add ",(0,s.kt)("a",{parentName:"p",href:"https://vcrpy.readthedocs.io/en/latest/advanced.html#register-your-own-request-matcher"},"custom request macthers")," to Cornell.\nThis can be easily done using the wrapper we created in the above example, with the ",(0,s.kt)("inlineCode",{parentName:"p"},"additional_vcr_matchers")," param:"),(0,s.kt)("pre",null,(0,s.kt)("code",{parentName:"pre",className:"language-python"},'#!/usr/bin/env python\n\nimport click\nimport json\nfrom vcr.util import read_body\nfrom cornell.cornell_server import CornellCmdOptions, start_cornell\nfrom cornell.cornell_helpers import json_in_headers\nfrom cornell.custom_matchers import requests_match_conditions\n\n\n# Custom Matcher\n@requests_match_conditions(json_in_headers, lambda request: request.body)\ndef vcr_json_custom_body_matcher(received_request, cassette_request):\n    received_request_dict = json.loads(read_body(received_request))\n    cassette_request_dict = json.loads(read_body(cassette_request))\n    if received_request_dict == cassette_request_dict or "special_params" not in received_request_dict:\n        return True\n    return is_specially_matched(received_request_dict, cassette_request_dict)\n\n\n@click.command(cls=CornellCmdOptions)\ndef start_mock_service(**kwargs):\n    start_cornell(additional_vcr_matchers=[vcr_json_custom_body_matcher], **kwargs)\n\n\nif __name__ == "__main__":\n    start_mock_service()\n')),(0,s.kt)("p",null,"In this example, we've added ",(0,s.kt)("inlineCode",{parentName:"p"},"vcr_json_custom_body_matcher")," as an ",(0,s.kt)("inlineCode",{parentName:"p"},"additional_vcr_matchers"),".\nNotice that Cornell also provides the ",(0,s.kt)("inlineCode",{parentName:"p"},"requests_match_conditions")," decorator, in case you'd want to activate your matcher only under specific circumstances."),(0,s.kt)("p",null,(0,s.kt)("strong",{parentName:"p"},"Note"),": If you're adding a custom matcher that actually implements standard protocols that can be widely used, kindly consider adding it as ",(0,s.kt)("a",{parentName:"p",href:"https://github.com/hiredscorelabs/cornell"},"PR")," to Cornell.\nYour contribution will be really appreciated!"))}u.isMDXComponent=!0}}]);